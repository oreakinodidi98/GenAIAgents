from dotenv import load_dotenv
import sys
import asyncio
from langchain.chat_models import init_chat_model
from pprint import pprint
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from pydantic import BaseModel
from langchain.tools import tool
from typing import Dict, Any
from tavily import TavilyClient
from langgraph.checkpoint.memory import InMemorySaver  
from ipywidgets import FileUpload
from IPython.display import display
import base64
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

# Local MCP configuration
client = MultiServerMCPClient(
    {
        "local_server": {
                "transport": "stdio",
                "command": "python",
                "args": ["Langchain/module2/01_mcp_agent.py"],
            }
    }
)
# get tools
tools = await client.get_tools()

# get resources
resources = await client.get_resources("local_server")

# get prompts
prompt = await client.get_prompt("local_server", "prompt")
prompt = prompt[0].content

# initialise tavily client
tavily_client = TavilyClient()

@tool
def web_search(query: str) -> Dict[str, Any]:
    """Search the web for information"""
    return tavily_client.search(query)

# initialise a model, with customization
gpt_model = init_chat_model(
    model="gpt-5-nano",
    # Kwargs passed to the model:
    temperature=1.0
    )
# create system prompt
system_prompt = """
You are a Orchestrator Agent

You are used for demo purposes 

"""
# create agent with system prompt and tool, using checkpointer to save the agent's memory in the InMemorySaver which is a simple in-memory storage for checkpoints.
chefagent = create_agent(model = gpt_model,
                     system_prompt=system_prompt,
                     tools=[ web_search, *tools],
                     checkpointer=InMemorySaver(),
)

# invoke the agent with a prompt and get response
question = HumanMessage(content="Tell me about the langchain-mcp-adapters library")
# Config for thread id
config = {"configurable": {"thread_id": "1"}}
# saving a snapshot of the stat at the end of each run and grouping it with the tread id
response = chefagent.invoke(
    {"messages": [question]},
    config=config
)

pprint(response)
print(response['messages'][-1].content)