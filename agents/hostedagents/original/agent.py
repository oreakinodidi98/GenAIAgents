from dotenv import load_dotenv
import os
import asyncio

#from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential

#from agent_framework import Agent, Message, Content
from agent_framework import Agent, Message, Content
from agent_framework.azure import AzureAIAgentClient, AzureAISearchContextProvider

load_dotenv() # Load environment variables from .env file

AZURE_AI_PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_AI_CHAT_DEPLOYMENT_NAME")
AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
#AZURE_OPENAI_KEY = os.getenv("AZURE_AI_API_KEY")

# agent instructions
AGENT_INSTRUCTIONS = """You are an HR Specialist Agent for The University of West London.
Answer questions about HR policies, PTO, benefits, and employee handbook using the knowledge base.
Be specific and cite sources when possible."""

# initialise agent
async def run_agent(query: str) -> str:
    """Run the HR agent with a query."""
    async with DefaultAzureCredential() as credential:
        async with (
            AzureAIAgentClient(
                project_endpoint=AZURE_AI_PROJECT_ENDPOINT,
                model_deployment_name=AZURE_OPENAI_DEPLOYMENT,
                credential=credential,
            ) as client,
            AzureAISearchContextProvider(
                endpoint=AZURE_AI_SEARCH_ENDPOINT,
                knowledge_base_name="ai-search-uwl",
                credential=credential,
                mode="agentic",
                knowledge_base_output_mode="answer_synthesis",
            ) as agent_context,
        ):
            agent = Agent(
                client=client,
                context_provider=agent_context,
                instructions=AGENT_INSTRUCTIONS,
            )

            message = Message(role="user", contents=[Content.from_text(query)])

            response = await agent.run(message)
            return response.text

async def main():
   
    print("\nHR Agent (ai-search-uwl)")
    print("=" * 50)

    query = "What is the PTO policy?"
    print(f"\nQuery: {query}")

    response = await run_agent(query)
    print(f"\nResponse:\n{response}")

if __name__ == "__main__":
    asyncio.run(main())
