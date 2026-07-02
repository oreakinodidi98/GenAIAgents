# This is a demo script to show how to use the ChatOpenAI model from
# langchain_openai and create a simple agent using LangChain.
from langchain_openai import ChatOpenAI
# Use to create an agent from LangChain.
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
# Async CosmosDBSaver checkpointer from langchain-azure-cosmosdb persists
# LangGraph state (messages, tool calls, etc.) into Azure Cosmos DB.
from langchain_azure_cosmosdb import CosmosDBSaver


import os
import asyncio
from uuid import uuid4
from dotenv import load_dotenv
from pydantic import SecretStr

# load environment variables from .env file
load_dotenv()

# function to test if environment variables are set
def require_env(name: str) -> str:
    """Return a required environment variable or fail fast with a clear message."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

# retrieve required environment variables
llm_model_deployment_name = require_env('LLM_MODEL_DEPLOYMENT_NAME_CHATGPT')
foundry_api_key = require_env('FOUNDRY_API_KEY')
foundry_endpoint = require_env('FOUNDRY_ENDPOINT')
cosmosdb_endpoint = require_env('COSMOSDB_ENDPOINT')

# create a ChatOpenAI model instance with streaming enabled
model = ChatOpenAI(
    base_url=f"{foundry_endpoint}/openai/v1",
    api_key=SecretStr(foundry_api_key),
    model=llm_model_deployment_name,
    streaming=True, # streaming to get output as it is written by llm
    max_completion_tokens=512 # specified limit to 512
)

# test if agent can be created and run with the LLM model
# Done by invoking model with test prompt and stream the output
# prompt = "tell me about your self"
# response = model.stream([HumanMessage(content=prompt)])

# # print the streamed response
# for chunk in response:
#     print(chunk.content, end="", flush=True)

# key for short term memory, every message in a conversation thread is saved to CosmosDB, so the agent can recall earlier messages in the same thread
# Force AAD auth path for CosmosDBSaver. This is required when Cosmos DB
# has Local Authorization disabled.
os.environ.pop("COSMOSDB_KEY", None)
question1 = "What is 7 multiplied by 13?"
question2 = "What is the answer to the previous question plus 10?"

# Test multi turn conversation with the agent, the agent will remember earlier messages in the same thread
async def run_agent():
    async with CosmosDBSaver.from_conn_info(
        endpoint=cosmosdb_endpoint,
        database_name="langgraph-memory",
        container_name="checkpoints",
    ) as checkpointer:
        # Create an agent that uses the LLM model to answer questions with memory.
        agent = create_agent(
            model=model,
            tools=[],
            middleware=[],
            checkpointer=checkpointer,
        )

        # Use a unique thread_id per run so each run has isolated memory.
        thread_id = f"demo-thread-{uuid4()}"
        config = {"configurable": {"thread_id": thread_id}}
        print(f"Using thread_id: {thread_id}")

        # test the agent with a simple question that requires reasoning and tool usage
        response1 = await agent.ainvoke(
            {"messages": [HumanMessage(content=question1)]},
            config=config,
        )
        print("Agent response to question 1:")
        print(response1["messages"][-1].content)

        # test the agent with a follow up question, the agent should remember the earlier message in the same thread
        response2 = await agent.ainvoke(
            {"messages": [HumanMessage(content=question2)]},
            config=config,
        )
        print("Agent response to question 2:")
        print(response2["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(run_agent())