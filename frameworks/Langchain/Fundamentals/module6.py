from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from random import randint
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import asyncio
# checkpoint
from langchain_azure_cosmosdb import CosmosDBSaverSync
# list all documents in the CosmosDB container to verify that conversation state is being saved
from azure.cosmos import CosmosClient
import json
# summarize message history in an agent, use the built-in SummarizationMiddleware
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig

from dotenv import load_dotenv
load_dotenv()

# Define custom tools for the agent
@tool
def get_weather(location: str) -> str:
    """Get the current weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    temp = randint(10, 30)
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {temp}°C."
# Define another custom tool for the agent
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together.

    Args:
        a: first number
        b: second number
    """
    return a * b

async def main():
    # Test environment variables
    print("endpoint:", os.getenv("FOUNDRY_ENDPOINT"))
    print("deployment:", os.getenv("LLM_MODEL_DEPLOYMENT_NAME"))
    print("CosmosDB Endpoint:", os.getenv("COSMOSDB_ENDPOINT"))
    print("CosmosDB Key:", os.getenv("COSMOSDB_KEY"))
    

    # define tools for the agent
    tools = [get_weather, multiply]
    print("Registered tools:", [t.name for t in tools])

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
    response = model.stream([HumanMessage(content="Tell me about Nigeria.")])
    # print response chunks as they arrive
    for chunk in response:
        print(chunk.content, end="", flush=True)
    
    # initialise CosmosDB saver
    print(f"\ninitialising CosmosDB checkpointer...")
    checkpointer = CosmosDBSaverSync(
        database_name="langgraph-memory",
        container_name="checkpoints",
        endpoint=os.getenv("COSMOSDB_ENDPOINT"),
        key=os.getenv("COSMOSDB_KEY"),
    )
    print(f"\nCosmosDB checkpointer initialised.")


    # use this for POC, as it stores memory in-memory rather than in CosmosDB
    memory_saver = InMemorySaver()

    # Use a unique thread_id — all messages with the same thread_id share memory
    print(f"\nusing thread_id: demo-thread-1")
    config = {"configurable": {"thread_id": "demo-thread-1"}}
    
    print(f"\ncreating agent...")
    # create agent with the llm model, tools, middleware, and checkpointer
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="You are a helpful Solutions architect running a demo with Langchain and CosmosDB.",
        middleware=[SummarizationMiddleware(
            # can use different model for summerisation if wanted
            model=model,
            trigger=("tokens", 4000),
            keep=("messages", 20)
        )],
        checkpointer=checkpointer,
    )

    print(f"\ngetting response from agent in streaming mode...")
    # get response from agent in streaming mode, adding thread_id from config
    async for step in agent.astream(
        {"messages": [HumanMessage(content="This is a Demo. My name is Ore and i am a CSA. Tell me about yourself")]},
        config=config,
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print()
    
    # ask agent to multiply two numbers
    async for step in agent.astream(
        {"messages": [HumanMessage(content="Multiply 6 by 7")]},
        config=config,
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

    # ask agent about the weather
    async for step in agent.astream(
        {"messages": [HumanMessage(content="I live in UK. What's the weather like in Amsterdam?")]},
        config=config,
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

    # ask agent about my name
    async for step in agent.astream(
        {"messages": [HumanMessage(content="What's my name and where do i live?")]},
        config=config,
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print()
    # Create new thread
    print(f"\nusing thread_id: demo-thread-2")
    new_config = {"configurable": {"thread_id": "demo-thread-2"}}
    async for step in agent.astream(
            {"messages": [HumanMessage(content="What's my name and where do i live?")]},
            config=new_config,
            stream_mode="values"
        ):
            step["messages"][-1].pretty_print()

    print(f"\nlisting all documents in CosmosDB container...")
    client = CosmosClient(os.getenv("COSMOSDB_ENDPOINT"), os.getenv("COSMOSDB_KEY"))
    database = client.get_database_client("langgraph-memory")
    container = database.get_container_client("checkpoints")
    for item in container.read_all_items():
        print(json.dumps(item, indent=2))

if __name__ == "__main__":
    asyncio.run(main())