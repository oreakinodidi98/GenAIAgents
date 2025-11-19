from dotenv import load_dotenv
import os
import json
import asyncio
import httpx
from azure.identity import AzureCliCredential,DefaultAzureCredential
from pydantic import Field
from agent_framework.azure import AzureOpenAIResponsesClient, AzureOpenAIChatClient
from typing import Annotated
from pydantic import Field
from agent_framework import ai_function,TextContent, FunctionCallContent, FunctionResultContent, FunctionApprovalRequestContent, ChatMessage, Role
import openmeteo_requests
from retry_requests import retry
import pandas as pd
import requests_cache

load_dotenv() # Load environment variables from .env file
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_AI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_AI_CHAT_DEPLOYMENT_NAME")

#when we get to this function/tool call we always require approval
@ai_function(approval_mode="always_require")
# define a function (tool) to fetch stock prices
def fetch_stock_price(symbol: str) -> float:
    """Fetch stock price for a given symbol."""
    # Simulate an API call to fetch stock prices
    #await asyncio.sleep(1)  # Simulate network 
    print(f"📈 Fetching stock price for {symbol}...")
    return 100.0  # Return a dummy stock price

# define a function to get weather information
def fetch_weather_info(
    location: Annotated[str, Field(description="The location to get weather information for")]
) -> str:
    """Fetch weather information for a given location."""
    # Simulate an API call to fetch weather information
    # asyncio.sleep(1)  # Simulate network delay
    print(f"🌤️ Fetching weather for {location}...")
    return f"The weather in {location} is sunny with a high of 75°F."  # Return dummy weather info

#when we get to this function/tool call we always require approval
@ai_function(approval_mode="always_require")
# define real time weather fetcher
def fetch_real_time_weather(
    latitude: Annotated[float, Field(description="The latitude of the location")],
    longitude: Annotated[float, Field(description="The longitude of the location")]
) -> str:
    """Fetch real-time weather information from Open-Meteo API for given coordinates."""
    print(f"🌦️ Fetching real-time weather for {latitude}, {longitude}...")

    try:
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Configure API request parameters
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m,relative_humidity_2m",
            "timezone": "auto",
        }
        
        print(f"📡 Making API request...")  # DEBUG
        # Make API request
        responses = openmeteo.weather_api(url, params=params)
        # Process first location
        response = responses[0]
        print(f"✅ Got response from API")  # DEBUG
        
        # Get current weather data
        current = response.Current()
        current_temp = current.Variables(0).Value()  # temperature_2m
        current_wind = current.Variables(1).Value()  # wind_speed_10m
        current_humidity = current.Variables(2).Value()  # relative_humidity_2m
        
        # Format response
        result = f"""Weather for coordinates ({latitude}°N, {longitude}°E):
Temperature: {current_temp:.1f}°C
Wind Speed: {current_wind:.1f} m/s
Humidity: {current_humidity:.0f}%
Timezone: {response.Timezone()} ({response.TimezoneAbbreviation()})
Elevation: {response.Elevation()} m"""
        
        return result
        
    except Exception as e:
        print(f"❌ Error details: {type(e).__name__}: {str(e)}")  # DEBUG
        import traceback
        traceback.print_exc()  # Print full traceback
        return f"Error fetching weather data: {str(e)}"
        
# initialise a chat agent with azure openai response and a toolset
agent = AzureOpenAIChatClient(
         endpoint=AZURE_OPENAI_ENDPOINT,
         api_key=AZURE_OPENAI_KEY,
         deployment_name=AZURE_OPENAI_DEPLOYMENT
).create_agent(
        model=AZURE_OPENAI_DEPLOYMENT,
        name="weather-agent",
        instructions="You are a helpful agent that responds to user queries.",
        tools=[fetch_stock_price, fetch_weather_info, fetch_real_time_weather] 
)

async def main():
    # #code to run as a stream 
    # async for update in agent.run_stream("Hello, can you tell me what the weather is in London and the current stock price for AAPL also What's the weather at latitude 51.5074 and longitude -0.1278??"):
    #     #print(f"Content count: {len(update.contents)}")
    #     #print(f"update type: {type(update)}")
    #     if update.text:
    #         print(update, end='', flush=True)

    async for update in agent.run_stream("Hello, can you tell me what the weather is in London and the current stock price for AAPL also What's the weather at latitude 51.5074 and longitude -0.1278??"):
        for content in update.contents:
            print(f"Content type: {type(content)}")
            if isinstance(content, TextContent):
                print(f"Text : {content.text}")
            elif isinstance(content, FunctionCallContent):
                print(f"function call: {content.name}")
                print(f"Call ID: {content.call_id}")
                print(f"Arguments: {content.arguments}")
            elif isinstance(content, FunctionResultContent):
                print(f"Function results: {content.result}")
            elif isinstance(content, FunctionApprovalRequestContent):
                print(f"Function Approval Call:{content.function_call.name}")
                print(f"Arguments:{content.function_call.arguments}")

    if update.user_input_requests:
        for user_input_needed in update.user_input_requests:
            print(f"Function:{user_input_needed.function_call.name}")
            print(f"Arguments:{user_input_needed.function_call.arguments}")
    
    user_approval= True
    approval_message = ChatMessage(role="user", contents=[user_input_needed.create_response(user_approval)])

    # final_result = await agent.run([
    #     "Hello, can you tell me what the weather is in London and the current stock price for AAPL also What's the weather at latitude 51.5074 and longitude -0.1278??",
    #     ChatMessage(role=Role.ASSISTANT, contents=[user_input_needed]),
    #     approval_message        
    # ])
    # print(final_result)

    print("--- Now continuing with approval ---")

    async for update in agent.run_stream(["Hello, can you tell me what the weather is in London and the current stock price for AAPL also What's the weather at latitude 51.5074 and longitude -0.1278?",
        ChatMessage(role=Role.ASSISTANT, contents=[user_input_needed]),
        approval_message
    ]):
        for content in update.contents:
            print(f"Content type: {type(content)}")
            if isinstance(content, TextContent):
                print(f"Text : {content.text}")
            elif isinstance(content, FunctionCallContent):
                print(f"function call: {content.name}")
                print(f"Call ID: {content.call_id}")
                print(f"Arguments: {content.arguments}")
            elif isinstance(content, FunctionResultContent):
                print(f"Function results: {content.result}")
            elif isinstance(content, FunctionApprovalRequestContent):
                print(f"Function Approval Call:{content.function_call.name}")
                print(f"Arguments:{content.function_call.arguments}")

if __name__ == "__main__":
    asyncio.run(main())
