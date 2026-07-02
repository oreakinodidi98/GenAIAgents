# This is a demo script to show how to use the ChatOpenAI model from
# langchain_openai and create a simple agent using LangChain.
from langchain_openai import ChatOpenAI
# Use to create an agent from LangChain.
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
#To summarize message history in an agent, use the built-in SummarizationMiddleware
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig


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

checkpointer = InMemorySaver()

#  creating a very sample Agent that uses the LLM model to answer questions.
agent = create_agent(
    model=model,
    tools=[],
    middleware=[
        SummarizationMiddleware(
            model=model,
            trigger=("tokens", 4000),
            keep=("messages", 20),
        )
    ],
    checkpointer=checkpointer,
)

# Use a unique thread_id per run so each run has isolated memory.
thread_id = f"demo-thread-{uuid4()}"
config = {"configurable": {"thread_id": thread_id}}
question1 = "hi, my name is Ore?"
question2 = "write a short poem about cats"
question3 = "now do the same but for dogs"
question4 = "what's my name?"

# function to run the agent asynchronously
async def run_agent() -> None:
    print(f"Using thread_id: {thread_id}")

    for idx, question in enumerate([question1, question2, question3], start=1):
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=question)]},
            config=config,
        )
        print(f"Agent response to question {idx}:")
        print(response["messages"][-1].content)

    final_response = await agent.ainvoke(
        {"messages": [HumanMessage(content=question4)]},
        config=config,
    )
    print("Agent response to question 4:")
    print(final_response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(run_agent())