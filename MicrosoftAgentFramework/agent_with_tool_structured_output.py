from dotenv import load_dotenv
import os
import json
import asyncio
from azure.identity import AzureCliCredential,DefaultAzureCredential
from pydantic import Field, BaseModel
from agent_framework.azure import AzureOpenAIResponsesClient, AzureOpenAIChatClient
from typing import Annotated
from pydantic import Field
import openmeteo_requests
from retry_requests import retry
import pandas as pd
import requests_cache

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

# # define a function to get weather information
# def fetch_weather_info(
#     location: Annotated[str, Field(description="The location to get weather information for")]
# ) -> str:
#     """Fetch weather information for a given location."""
#     # Simulate an API call to fetch weather information
#     # asyncio.sleep(1)  # Simulate network delay
#     print(f"🌤️ Fetching weather for {location}...")
#     return f"The weather in {location} is sunny with a high of 75°F."  # Return dummy weather info

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

# initialise a chat agent with azure openai response and a toolset
agent = AzureOpenAIChatClient(
         endpoint=AZURE_OPENAI_ENDPOINT,
         api_key=AZURE_OPENAI_KEY,
         deployment_name=AZURE_OPENAI_DEPLOYMENT
).create_agent(
        model=AZURE_OPENAI_DEPLOYMENT,
        name="weather-agent",
        instructions="You are a helpful assistant that figures out the city from the information provided and also returns the current weather",
        tools=[fetch_stock_price, fetch_weather_info] 
)

async def main():
   
   print(f"Created agent with ID: {agent.id}")
   result = await agent.run(
       "Im at the CN tower",
       response_format=CityInfo
       )
   #result = await agent.run("Hello, can you tell me what the weather at latitude 51.5074 and longitude -0.1278?")
   if result.value:
       City_Info = result.value
       print("\n🏙️ City Information:")
       print(f"Name: {City_Info.name}")
       print(f"Country: {City_Info.country}")
       print(f"Population: {City_Info.population}")
       print(f"Weather: {City_Info.weather}")
   else:
       print("No structured output received from the agent.")

if __name__ == "__main__":
    asyncio.run(main())
