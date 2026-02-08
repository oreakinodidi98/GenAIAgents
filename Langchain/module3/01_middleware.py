from typing_extensions import runtime
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.chat_models import init_chat_model
from pprint import pprint
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver  
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import tool
from typing import Dict, Any
from langchain.agents import AgentState
from langchain.tools import ToolRuntime
from langchain.messages import HumanMessage, ToolMessage ,AIMessage
from langgraph.types import Command
from langchain.agents.middleware import SummarizationMiddleware


# initialise a model, with customization
gpt_model = init_chat_model(
    model="gpt-5-nano",
    # Kwargs passed to the model:
    temperature=1.0
    )
summary_model = init_chat_model(
    model="gpt-4o-mini",
    # Kwargs passed to the model:
    temperature=0.1
    )
# agent with summarization middleware that triggers when the total tokens in the messages exceed 100 tokens, and keeps the last message and the summary in the context. The summarization is done by gpt-4o-mini model.
agent = create_agent(
    model=gpt_model,
    checkpointer=InMemorySaver(),
    middleware=[
        SummarizationMiddleware(
            model=summary_model,
            trigger=("tokens", 100),
            keep=("messages", 1)
        )
    ],
)

response = agent.invoke(
    {"messages": [
        HumanMessage(content="What is the capital of the moon?"),
        AIMessage(content="The capital of the moon is Lunapolis."),
        HumanMessage(content="What is the weather in Lunapolis?"),
        AIMessage(content="Skies are clear, with a high of 120C and a low of -100C."),
        HumanMessage(content="How many cheese miners live in Lunapolis?"),
        AIMessage(content="There are 100,000 cheese miners living in Lunapolis."),
        HumanMessage(content="Do you think the cheese miners' union will strike?"),
        AIMessage(content="Yes, because they are unhappy with the new president."),
        HumanMessage(content="If you were Lunapolis' new president how would you respond to the cheese miners' union?"),
        ]},
    {"configurable": {"thread_id": "1"}}
)

pprint(response)
print(response["messages"][0].content)