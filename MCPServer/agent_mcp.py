from dotenv import load_dotenv
import os
import json
import asyncio
from azure.identity import AzureCliCredential,DefaultAzureCredential
from pydantic import Field
from agent_framework.azure import AzureOpenAIResponsesClient, AzureOpenAIChatClient
from typing import Annotated
from pydantic import Field
import anyio
from mcp.server.stdio import stdio_server

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

# define a function to get weather information
def fetch_weather_info(
    location: Annotated[str, Field(description="The location to get weather information for")]
) -> str:
    """Fetch weather information for a given location."""
    # Simulate an API call to fetch weather information
    # asyncio.sleep(1)  # Simulate network delay
    print(f"🌤️ Fetching weather for {location}...")
    return f"The weather in {location} is sunny with a high of 75°F."  # Return dummy weather info

# initialise a chat agent with azure openai response and a toolset
agent = AzureOpenAIChatClient(
         endpoint=AZURE_OPENAI_ENDPOINT,
         api_key=AZURE_OPENAI_KEY,
         deployment_name=AZURE_OPENAI_DEPLOYMENT
).create_agent(
        model=AZURE_OPENAI_DEPLOYMENT,
        name="weather-agent",
        instructions="You are a helpful agent that responds to user queries.",
        tools=[fetch_stock_price, fetch_weather_info] 
)

# to turn agent to MCP server 
server = agent.as_mcp_server()

# create run method to allow agent to listen for requests and respond
async def run():
    print("Starting MCP Server...")
    async def handle_stdin():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    await handle_stdin()

# async def main():
   
#    print(f"Created agent with ID: {agent.id}")
#    #print(await agent.run("Hello, can you tell what the weather is in london and the current stock price?"))
#    # Test the agent with tool usage
#    result = await agent.run("Hello, can you tell me what the weather is in London and the current stock price for AAPL?")
#    print("\n🤖 Agent Response:")
#    print(result)

if __name__ == "__main__":
    anyio.run(run)