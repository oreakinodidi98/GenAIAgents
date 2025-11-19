from dotenv import load_dotenv
import os
import json
import asyncio
import openmeteo_requests
from retry_requests import retry
import pandas as pd
import requests_cache
from azure.identity import AzureCliCredential,DefaultAzureCredential
from pydantic import Field, BaseModel
from typing import Annotated
from pydantic import Field
from agent_framework.azure import AzureOpenAIResponsesClient, AzureOpenAIChatClient
from agent_framework import AgentExecutor, AgentRunUpdateEvent , WorkflowBuilder, WorkflowOutputEvent, WorkflowStatusEvent, WorkflowViz

class CityInfo(BaseModel):
    """Structured output model for city information."""
    name: str = Field(description="Name of the city")
    country: str = Field(description="Country where the city is located")
    population: int = Field(description="Population of the city")
    weather: str = Field(description="Current weather description in the city")

load_dotenv() # Load environment variables from .env file
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_AI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_AI_CHAT_DEPLOYMENT_NAME")

# define a function (tool) to fetch stock prices
def fetch_stock_price(symbol: str) -> float:
    """Fetch stock price for a given symbol."""
    # Simulate an API call to fetch stock prices
    #await asyncio.sleep(1)  # Simulate network 
    print(f"📈 Fetching stock price for {symbol}...")
    return 100.0  # Return a dummy stock price

# define real time weather fetcher
def fetch_weather_info(
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
        print(f"🌤️ Fetching weather for for coordinates ({latitude}°N, {longitude}°E...")
        return result
        
    except Exception as e:
        print(f"❌ Error details: {type(e).__name__}: {str(e)}")  # DEBUG
        import traceback
        traceback.print_exc()  # Print full traceback
        return f"Error fetching weather data: {str(e)}"



async def main() -> None:
   # create a chat client with azure openai response and a toolset
    chat_client = AzureOpenAIChatClient(
            endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY,
            deployment_name=AZURE_OPENAI_DEPLOYMENT
    )

    try:
        # create first agent for workflow
        city_info_agent = AgentExecutor(
            chat_client.create_agent(
                model=AZURE_OPENAI_DEPLOYMENT,
                name="city-info-agent",
                instructions="You are a helpful assistant that figures out the city from the information provided and also returns the current weather",
                tools=[fetch_weather_info],
                response_format=CityInfo    
                )
        )
        # create second agent for workflow
        tourist_recommendation_agent = AgentExecutor(
            chat_client.create_agent(
                model=AZURE_OPENAI_DEPLOYMENT,
                name="tourist-recommendation-agent",
                instructions=(
                    "You are a helpful assistant that provides tourist recommendations based on a city." \
                    "your input is a structured CityInfo object containing city name, country, population, and current weather." \
                    "Based on this information, suggest top tourist attractions, local cuisine, and best times to visit." \
                    "Do not recommend places that are closed or not accessible currently." \
                    "do not recommend the place you are already in." \
                    "Format your response in a friendly and engaging manner."
                )   
                )
        )
        
        # create workflow by chaining agents using edge
        workflow= WorkflowBuilder().set_start_executor(city_info_agent).add_edge(city_info_agent, tourist_recommendation_agent).build()
        print(f"Created workflow")

        #visualise workflow
        viz= WorkflowViz(workflow)
        doc_diagram = viz.save_svg("docs/agents_in_workflow_diagram.svg")
        print("Saved workflow diagram as 'agents_in_workflow_diagram.svg'")

        # run workflow
        events = workflow.run_stream(
            "I'm at the CN tower"
        )

        last_executor_id: str | None = None

        async for event in events:
            if isinstance(event, AgentRunUpdateEvent):
                #print(f"\n🔄 Workflow Status Update: {event}")
                # handle streamming updates from agents
                if event.executor_id != last_executor_id:
                    if last_executor_id is not None:
                        print("\n--- Switching to next agent ---\n")
                    print(f"🤖 Agent ({event.executor_id}) Response Update:")
                    last_executor_id = event.executor_id
                print(event.data, end='', flush=True)
            elif isinstance(event, WorkflowStatusEvent):
                print("\n🔔 Workflow Status Event:")
                print(event)
            
    finally:
        pass

if __name__ == "__main__":
    asyncio.run(main())
