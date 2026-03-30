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

load_dotenv()

# create square root tool 
@tool
def square_root(x: float) -> float:
    """Calculate the square root of a number"""
    return x ** 0.5
# create square tool
@tool
def square(x: float) -> float:
    """Calculate the square of a number"""
    return x ** 2


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
You are a helpful assistant who can call subagents to calculate the square root or square of a number.
"""
# create sub agent 1 system prompt
sub_agent_1_system_prompt = """
You are a Sub Agent 1
You are used for demo purposes
You are a helpful assistant who can calculate the square root of a number.
"""

sub_agent_2_system_prompt = """
You are a Sub Agent 2
You are used for demo purposes
You are a helpful assistant who can calculate the square of a number.
"""

# Create Sub agent 1
sub_agent_1 = create_agent(model = gpt_model,
                     system_prompt=sub_agent_1_system_prompt,
                     tools=[square_root],
                     checkpointer=InMemorySaver(),
)
sub_agent_2= create_agent(model = gpt_model,
                     system_prompt=sub_agent_2_system_prompt,
                     tools=[square],
                     checkpointer=InMemorySaver(),
)

# tool to call sub agent 1
@tool
def call_subagent_1(x: float) -> float:
    """Call subagent 1 in order to calculate the square root of a number"""
    response = sub_agent_1.invoke({"messages": [HumanMessage(content=f"Calculate the square root of {x}")]})
    return response["messages"][-1].content
# tool to call sub agent 2
@tool
def call_subagent_2(x: float) -> float:
    """Call subagent 2 in order to calculate the square of a number"""
    response = sub_agent_2.invoke({"messages": [HumanMessage(content=f"Calculate the square of {x}")]})
    return response["messages"][-1].content

# create agent with system prompt and tool, using checkpointer to save the agent's memory in the InMemorySaver which is a simple in-memory storage for checkpoints.
master_agent = create_agent(model = gpt_model,
                     system_prompt=system_prompt,
                     tools=[call_subagent_1, call_subagent_2],
                     checkpointer=InMemorySaver(),
)
# invoke the agent with a prompt and get response
question = "what is the square root of 16 and what is the square of 4?"

# Config for thread id
config = {"configurable": {"thread_id": "1"}}

# saving a snapshot of the stat at the end of each run and grouping it with the tread id
response = master_agent.invoke(
    {"messages": [HumanMessage(content=question)]},
    config=config,
)

pprint(response)
print(response['messages'][-1].content)