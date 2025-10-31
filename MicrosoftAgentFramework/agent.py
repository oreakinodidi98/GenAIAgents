from dotenv import load_dotenv
import os
import json
import asyncio
from azure.identity import AzureCliCredential,DefaultAzureCredential
from agent_framework.azure import AzureOpenAIResponsesClient, AzureOpenAIChatClient

load_dotenv() # Load environment variables from .env file
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_AI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_AI_CHAT_DEPLOYMENT_NAME")

# initialise a chat agent with azure openai response
agent = AzureOpenAIChatClient(
         endpoint=AZURE_OPENAI_ENDPOINT,
         api_key=AZURE_OPENAI_KEY,
         deployment_name=AZURE_OPENAI_DEPLOYMENT
).create_agent(
        model=AZURE_OPENAI_DEPLOYMENT,
        name="Joker-agent",
        instructions="You are a helpful agent that responds to user queries.",
)

async def main():
   
   print(f"Created agent with ID: {agent.id}")
   print(await agent.run("Hello, can you tell me a joke about london?"))

if __name__ == "__main__":
    asyncio.run(main())
