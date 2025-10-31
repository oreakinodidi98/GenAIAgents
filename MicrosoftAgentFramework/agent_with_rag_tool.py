from dotenv import load_dotenv
import os
import json
import asyncio
from azure.identity import AzureCliCredential,DefaultAzureCredential
from pydantic import Field
from agent_framework.azure import AzureOpenAIChatClient
from typing import Annotated
from azure.core.credentials import AzureKeyCredential
from openai import AsyncAzureOpenAI

from search_index_manager import SearchIndexManager



load_dotenv() # Load environment variables from .env file
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_AI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_AI_CHAT_DEPLOYMENT_NAME")

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

search_index_manager = SearchIndexManager(
    endpoint=SEARCH_ENDPOINT,
    credentials=azure_search_credential,
    model=AZURE_SEARCH_MODEL,
    api_key=SEARCH_API_KEY,
    index_name=SEARCH_INDEX_NAME,
    dimension=embed_dimensions,  # Use the defined variable
    embeddings_client=embeddings_client  # Use the defined variable
)

# define a function (tool) to fetch information from RAG
async def get_info(
    query: Annotated[str, Field(description="Get information from the RAG.")],
) -> str:
    """Get information from the RAG."""
    context = await search_index_manager.search(query)

    if context:
        print("📚 Retrieved context from RAG:")
        return context
    else:
        return "No information found."

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
        name="RAG-agent",
        instructions="You are a helpful assistant that retrieves info using tools to answer user's question.  If you can't find any information, say 'Sorry, I don't know.'",
        tools=[get_info, fetch_weather_info] 
)

async def main():
   
   try:
    await search_index_manager.ensure_index_created(
        vector_index_dimensions=embed_dimensions if embed_dimensions else 100)
    print(f"Created agent with ID: {agent.id}")
    
    # Test the agent with tool usage
    result = await agent.run("Hello, can you tell me what the weather is in London and the information you have access to with the get info tool regarding the latest VBD (Value Based Deliverable)?")
    print("\n🤖 Agent Response:")
    print(result)
   finally:
       await search_index_manager.close()
       await embeddings_client.close()

if __name__ == "__main__":
    asyncio.run(main())
