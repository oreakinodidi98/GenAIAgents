from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from random import randint
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import asyncio
# tools

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
    response = model.stream([HumanMessage(content="Tell me about yourself.")])

    # print response chunks as they arrive
    for chunk in response:
        print(chunk.content, end="", flush=True)

    print(f"\ncreating agent...")
    # create agent with the llm model
    agent = create_agent(
        model=model,
        tools=tools,
        middleware=[],
        checkpointer=None,
    )

    print(f"\ngetting response from agent in streaming mode...")
    # get response from agent in streaming mode
    async for step in agent.astream(
        {"messages": [HumanMessage(content="This is a Demo. Tell me about yourself")]},
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print()
    
    # ask agent to multiply two numbers
    async for step in agent.astream(
    {"messages": [HumanMessage(content="Multiply 6 by 7")]},
    stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

    # ask agent about the weather
    async for step in agent.astream(
    {"messages": [HumanMessage(content="What's the weather like in Amsterdam?")]},
    stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

if __name__ == "__main__":
    asyncio.run(main())