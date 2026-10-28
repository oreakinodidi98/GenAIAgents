from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from random import randint
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import asyncio
# mcp
from langchain_mcp_adapters.client import MultiServerMCPClient

from dotenv import load_dotenv
load_dotenv()

# Connect to the Microsoft Learn MCP server, public endpoint so no authentication is required
mcp_client = MultiServerMCPClient(
    {
        "microsoft-learn": {
            "url": "https://learn.microsoft.com/api/mcp",
            "transport": "http",
        }
    }
)

async def main():
    # Test environment variables
    print("endpoint:", os.getenv("FOUNDRY_ENDPOINT"))
    print("deployment:", os.getenv("LLM_MODEL_DEPLOYMENT_NAME"))

    # initialise model
    print(f"\ninitialising model...")
    model = ChatOpenAI(
        base_url=f"{os.getenv('FOUNDRY_ENDPOINT')}/openai/v1",
        #api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        api_key=get_bearer_token_provider(
            DefaultAzureCredential(), 
            "https://ai.azure.com/.default"
            ),
        model=os.getenv('LLM_MODEL_DEPLOYMENT_NAME'),
        streaming=True,
        max_completion_tokens=512
    )
    print(f"\nmodel initialised.")
    
    print(f"\ngetting response from model...")
    # get response from model
    response = model.stream([HumanMessage(content="Tell me about yourself.")])

    # print response chunks as they arrive
    for chunk in response:
        print(chunk.content, end="", flush=True)

    # Show tools exposed by Microsoft Learn and assign them to the agent through the tools parameter
    learn_tools = await mcp_client.get_tools()
    print(f"\nMicrosoft Learn MCP tools: {[t.name for t in learn_tools]}")
    
    print(f"\ncreating agent...")
    # create agent with the llm model
    learn_agent = create_agent(
        model=model,
        tools=learn_tools,
        middleware=[],
        checkpointer=None,
    )

    # ask agent question 
    async for step in learn_agent.astream(
    {"messages": [HumanMessage(content="How do I deploy a container app with GPU support on Azure Container Apps?")]},
    stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

if __name__ == "__main__":
    asyncio.run(main())