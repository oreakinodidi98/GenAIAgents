from langchain_openai import ChatOpenAI

from langchain.agents import create_agent # use to create agent from langchain
from langchain_core.messages import HumanMessage

import os
import asyncio
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

# create a ChatOpenAI model instance with streaming enabled
model = ChatOpenAI(
    base_url=f"{foundry_endpoint}/openai/v1",
    api_key=SecretStr(foundry_api_key),
    model=llm_model_deployment_name,
    streaming=True, # streaming to get output as it is written by llm
    max_completion_tokens=512 # specified limit to 512
)

# invoke model with test prompt and stream the output
prompt = "tell me about your self"
response = model.stream([HumanMessage(content=prompt)])

# print the streamed response
for chunk in response:
    print(chunk.content, end="", flush=True)

###### Use the LLM model in a Langchain Agent #####

#  creating a very sample Agent that uses the LLM model to answer questions.
agent = create_agent(
    model=model,
    tools=[],
    middleware=[],
    checkpointer=None,
)

# test the agent with a simple question
question = "What is the capital of France?"

# function to run the agent asynchronously and stream the output
async def run_agent() -> None:
    async for step in agent.astream(
        {"messages": [HumanMessage(content=question)]},
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print() # output has 2 sections the human message and the agent response, we print the last message which is the agent response


if __name__ == "__main__":
    asyncio.run(run_agent())