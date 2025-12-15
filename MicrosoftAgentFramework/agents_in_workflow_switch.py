from dotenv import load_dotenv
import os
import asyncio
import openmeteo_requests
from retry_requests import retry
import requests_cache
from azure.core.credentials import AzureKeyCredential
from search_index_manager import SearchIndexManager
from openai import AsyncAzureOpenAI
from pydantic import Field, BaseModel
from typing import Annotated, Any
from agent_framework.azure import AzureOpenAIResponsesClient, AzureOpenAIChatClient
from agent_framework import (
    AgentExecutor, 
    AgentRunUpdateEvent , 
    WorkflowBuilder, 
    WorkflowOutputEvent, 
    WorkflowStatusEvent, 
    WorkflowViz, 
    AgentExecutorResponse, 
    Case, 
    Default)

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
# RAG Search variables
SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
AZURE_SEARCH_MODEL = os.getenv("AZURE_SEARCH_MODEL")
# Define embedding dimensions
embed_dimensions = 1536
azure_search_credential = AzureKeyCredential(SEARCH_API_KEY)
# Create embeddings client that we can reference later
embeddings_client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-01"
)
# Create Search Index Manager
search_index_manager = SearchIndexManager(
    endpoint=SEARCH_ENDPOINT,
    credentials=azure_search_credential,
    model=AZURE_SEARCH_MODEL,
    api_key=SEARCH_API_KEY,
    index_name=SEARCH_INDEX_NAME,
    dimension=embed_dimensions,  # Use the defined variable
    embeddings_client=embeddings_client  # Use the defined variable
)
# define a function (tool) to fetch stock prices
def fetch_stock_price(symbol: str) -> float:
    """Fetch stock price for a given symbol."""
    # Simulate an API call to fetch stock prices
    #await asyncio.sleep(1)  # Simulate network 
    print(f"📈 Fetching stock price for {symbol}...")
    return 100.0  # Return a dummy stock price

# define a tool that will go to the rag
async def get_info(
    query: Annotated[str, Field(description="Get information from the RAG.")],
) -> str:
    """Get information from the RAG."""
    try:
        context = await search_index_manager.search(query)
        if context:
            print("📚 Retrieved context from RAG:")
            return context
        else:
            return "No information found."
    except Exception as e:
        print(f"❌ Error details: {type(e).__name__}: {str(e)}")  # DEBUG
        import traceback
        traceback.print_exc()  # Print full traceback
        return f"Error fetching information from RAG: {str(e)}"

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

# condition factory that retuns predicate matching a specific country
def get_country(expected_country: str):
    """Factory that returns a predicate matching a specific country."""
    def condition(
        message: Any
    ) -> bool:
        if not isinstance(message, AgentExecutorResponse):
            return False
        try:
            # Parse the CityInfo object from the agent's JSON response
            city_info = CityInfo.model_validate_json(message.agent_run_response.text)
            # Evaluate the condition based on country
            return city_info.country.lower() == expected_country.lower()
        except Exception:
            print("❌ Error parsing CityInfo from agent response.")  # DEBUG
            return False
    return condition

async def main() -> None:
   # create a chat client with azure openai response and a toolset
    chat_client = AzureOpenAIChatClient(
            endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY,
            deployment_name=AZURE_OPENAI_DEPLOYMENT
    )

    try:
        #initialise search index manager
        await search_index_manager.ensure_index_created(
            vector_index_dimensions=embed_dimensions if embed_dimensions else 100
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
        #create third agent for workflow with conditional RAG tool usage
        report_info_agent = AgentExecutor(
            chat_client.create_agent(
                model=AZURE_OPENAI_DEPLOYMENT,
                name="finance-report-info-agent",
                instructions=(
                    "You are a helpful assistant that provides detailed financial reports summaries." \
                    "If the user query requires specific information, use the get_info tool to fetch relevant data from the RAG." \
                    "If the information is not found in the RAG, respond with 'Sorry, I don't know.'" \
                    "Format your response clearly and concisely."
                ),
                tools=[get_info]
            )
        )
        #resturant agent
        restaurant_agent = AgentExecutor(
            chat_client.create_agent(
                model=AZURE_OPENAI_DEPLOYMENT,
                name="restaurant-recommendation-agent",
                instructions=(
                    "You are a helpful assistant that provides restaurant recommendations based on country and city." \
                    "your input is a structured CityInfo object containing city name, country, population, and current weather." \
                    "Based on this information, suggest top restaurants, local cuisine, and best times to visit." \
                    "Do not recommend places that are closed or not accessible currently." \
                    "do not recommend the place you are already in." \
                    "Format your response in a friendly and engaging manner."
                ),   
            )
        )
        
        # create workflow by chaining agents using edge
        workflow= (
            WorkflowBuilder()
            .set_start_executor(city_info_agent)
            .add_switch_case_edge_group(
                city_info_agent,
                [
                    Case(condition=get_country("Canada"), target=tourist_recommendation_agent),
                    Case(condition=get_country("United Kingdom"), target=restaurant_agent),
                    Default(target=report_info_agent)
                ]
            )
            .build()
        )

        print(f"Created workflow")
        #visualise workflow
        viz= WorkflowViz(workflow)
        doc_diagram = viz.save_svg("docs/switch_agents_in_workflow_diagram.svg")
        print("Saved workflow diagram as 'switch_agents_in_workflow_diagram.svg'")
        # run workflow
        events = workflow.run_stream(
            "I'm at the Big Ben tower, interested about Apple's financial reports hm"
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
        # close search index manager conections
        await search_index_manager.close()
        await embeddings_client.close()
        pass

if __name__ == "__main__":
    asyncio.run(main())
