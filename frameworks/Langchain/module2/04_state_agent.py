from dotenv import load_dotenv
import sys
import asyncio
from langchain.chat_models import init_chat_model
from pprint import pprint
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver  
from langchain_mcp_adapters.client import MultiServerMCPClient
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langchain.agents import AgentState
from langgraph.types import Command
from langchain.messages import ToolMessage


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

# context schema to fill in and then pass to the agent
# This is passed to the tool runtime so that the agent can use the context in the tools 
# And also update the context based on the tool outputs. 
# The context is also passed to the agent on each run, so that the agent can use the context to generate responses and not overload with redundant information.
@dataclass
class ColourContext:
    favourite_colour: str = "blue"
    least_favourite_colour: str = "yellow"

class CustomState(AgentState):
    favourite_colour: str

# create tools from tool runtime
@tool
def get_favourite_colour(runtime: ToolRuntime) -> str:
    """Get the favourite colour of the user"""
    return runtime.context.favourite_colour

@tool
def get_least_favourite_colour(runtime: ToolRuntime) -> str:
    """Get the least favourite colour of the user"""
    return runtime.context.least_favourite_colour

# for state agent needs to access state through tool runtime
@tool
def update_favourite_colour(favourite_colour: str, runtime: ToolRuntime) -> Command:
    """Update the favourite colour of the user in the state once they've revealed it."""
    return Command(update={
        "favourite_colour": favourite_colour, 
        "messages": [ToolMessage("Successfully updated favourite colour", tool_call_id=runtime.tool_call_id)]}
        )

# Also needs a tool to read state of favourite collour
@tool
def read_favourite_colour(runtime: ToolRuntime) -> str:
    """Read the favourite colour of the user from the state."""
    try:
        return runtime.state["favourite_colour"]
    except KeyError:
        return "No favourite colour found in state"


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
agent = create_agent(model = gpt_model,
                     system_prompt=system_prompt,
                     tools=[update_favourite_colour, read_favourite_colour],
                     context_schema=ColourContext, # passing the context schema to the agent    
                     checkpointer=InMemorySaver(),
)

# invoke the agent with a prompt and get response
question = HumanMessage(content="What is my favourite colour and least favourite colour?")
# Config for thread id
config = {"configurable": {"thread_id": "1"}}
# saving a snapshot of the stat at the end of each run and grouping it with the tread id
response = agent.invoke(
    {"messages": [question]},
    config=config,
    context=ColourContext()
)

pprint(response)
print(response['messages'][-1].content)