from dotenv import load_dotenv
import os
import json
import asyncio
from azure.identity import AzureCliCredential,DefaultAzureCredential
from pydantic import Field, BaseModel
from typing import Annotated
from pydantic import Field
from agent_framework.azure import AzureOpenAIResponsesClient, AzureOpenAIChatClient
from agent_framework import AgentExecutor, AgentRunUpdateEvent , WorkflowBuilder, WorkflowOutputEvent, WorkflowStatusEvent, WorkflowViz
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route

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




# create a chat client with azure openai response and a toolset
chat_client = AzureOpenAIChatClient(
        endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        deployment_name=AZURE_OPENAI_DEPLOYMENT
)

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

# convert workflow to agent
workflow_agent = workflow.as_agent()
# run this agent as tool as workflow agent doesnt have a MCP_server
workflow_tool = workflow_agent.as_tool(
name="city-info-and-tourist-recommendation-tool",
description="A tool that provides city information and tourist recommendations based on user input about their location"
)

# create a wrapper agent that uses the workflow as a tool
wrapper_agent = chat_client.create_agent(
    # model=AZURE_OPENAI_DEPLOYMENT,
    name="tourist-info-agent",
    instructions=(
        "You are a helpful assistant that provides city information and tourist recommendations based on user input about their location." \
        "Use the 'city-info-and-tourist-recommendation-tool' to get the information and recommendations for the user." \
        "Format your response in a friendly and engaging manner."
    ),
    tools=[workflow_tool]
)

# now expose wrapper as MCP server turn agent to MCP server 
server = wrapper_agent.as_mcp_server()
# create sse server
sse = SseServerTransport("/messages")

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

async def handle_messages(request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

# use starlette and 2 endpoint to run over SSE
app = Starlette(debug=True, 
    routes=[
        Route("/sse", handle_sse),
        Route("/messages", handle_messages, methods=["POST"])
    ]
)


if __name__ == "__main__":
    print("Starting server...")
    print("workflow: city-info-agent -> tourist-recommendation-agent")
    uvicorn.run(app, host="0.0.0.0", port=8010)