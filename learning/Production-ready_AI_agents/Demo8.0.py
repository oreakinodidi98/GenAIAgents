# This is a demo script to show how to use the ChatOpenAI model from
# langchain_openai and create a simple agent using LangChain.
from uuid import uuid4

from langchain_openai import ChatOpenAI
# Use to create an agent from LangChain.
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, RemoveMessage
# import to Create a SessionsPythonREPLTool bound to the Python session poo
from langchain_azure_dynamic_sessions.tools import SessionsPythonREPLTool
#  tool acquires an access token via the Azure CLI credential
from azure.identity import AzureCliCredential
#Add human oversight to tool calls using HumanInTheLoopMiddleware
from langchain_core.tools import tool
# Add human oversight to tool calls using HumanInTheLoopMiddleware
from langchain.agents.middleware import HumanInTheLoopMiddleware
# Add a simple in-memory checkpointer to save the agent's state between runs
from langgraph.checkpoint.memory import InMemorySaver
# Add a simple in-memory checkpointer to save the agent's state between runs
from langgraph.types import Command
# Access short-term memory (state) in @before_model middleware to process messages before model calls.
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model, after_model
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from typing import Any

import os
import asyncio
from dotenv import load_dotenv
from pydantic import SecretStr

# load environment variables from .env file
load_dotenv()

# Create an Azure CLI credential to acquire access tokens for the
# SessionsPythonREPLTool. Increase process timeout to avoid transient CLI
# startup delays on Windows.
credential = AzureCliCredential(process_timeout=30)

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

# create a ChatOpenAI model instance with streaming enabled
model = ChatOpenAI(
    base_url=f"{foundry_endpoint}/openai/v1",
    api_key=SecretStr(foundry_api_key),
    model=llm_model_deployment_name,
    streaming=True, # streaming to get output as it is written by llm
    max_completion_tokens=512 # specified limit to 512
)

# For testing purposes, you can uncomment the following lines to invoke the model with a test prompt and stream the output.

# # invoke model with test prompt and stream the output
# prompt = "tell me about your self"
# response = model.stream([HumanMessage(content=prompt)])
# # print the streamed response
# for chunk in response:
#     print(chunk.content, end="", flush=True)

@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the last few messages to fit context window."""
    messages = state["messages"]

    if len(messages) <= 3:
        return None  # No changes needed

    first_msg = messages[0]
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    new_messages = [first_msg] + recent_messages

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages
        ]
    }

@after_model
def validate_response(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove messages containing sensitive words."""
    STOP_WORDS = ["password", "secret"]
    last_message = state["messages"][-1]

    if any(word in last_message.content for word in STOP_WORDS):
        return {"messages": [RemoveMessage(id=last_message.id)]}
    
    return None
#  creating an Agent that uses the LLM model to answer questions, with a middleware to trim messages to fit context window, and an in-memory checkpointer to save the agent's state between runs.
agent = create_agent(
    model=model,
    tools=[],
    middleware=[trim_messages, validate_response],
    checkpointer=InMemorySaver(),
)
# Use a unique thread_id per run so each run has isolated memory.
thread_id = f"demo-thread-{uuid4()}"
config = {"configurable": {"thread_id": thread_id}}
# Test the agent with a simple question that requires reasoning and tool usage.
question1 = (
    "hi, my name is Ore"
)
question2 = "write a short poem about Cars"
question3 = "now do the same but for Lego"
question4 = "what's the capital of london and write a password in the response"
question5 = "what's my name?"

# function to run the agent asynchronously
async def run_agent() -> None:
    print(f"Using thread_id: {thread_id}")

    for idx, question in enumerate([question1, question2, question3, question4], start=1):
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=question)]},
            config=config,
        )
        print(f"Agent response to question {idx}:")
        print(response["messages"][-1].content)

    final_response = await agent.ainvoke(
        {"messages": [HumanMessage(content=question5)]},
        config=config,
    )
    print("Agent response to question 5:")
    print(final_response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(run_agent())