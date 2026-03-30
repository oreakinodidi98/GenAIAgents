from dotenv import load_dotenv
import sys
import asyncio
from langchain.chat_models import init_chat_model
from pprint import pprint
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver  

from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

# Online MCP configuration
client = MultiServerMCPClient(
    {
        "time": {
            "transport": "stdio",
            "command": "uvx",
            "args": [
                "mcp-server-time",
                "--local-timezone=America/New_York"
            ]
        }
    },
    {
        "mcpServers": {
            "playwright": {
            "command": "npx",
            "args": [
                "@playwright/mcp@latest"
        ]
        }
    }
    }
)

# get tools
tools = await client.get_tools()

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
                     tools=tools,
                     checkpointer=InMemorySaver(),
)

# invoke the agent with a prompt and get response
question = HumanMessage(content="Tell me about the langchain-mcp-adapters library and what time it is")
# Config for thread id
config = {"configurable": {"thread_id": "1"}}
# saving a snapshot of the stat at the end of each run and grouping it with the tread id
response = chefagent.invoke(
    {"messages": [question]},
    config=config
)

pprint(response)
print(response['messages'][-1].content)