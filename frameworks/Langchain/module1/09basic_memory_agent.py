from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pprint import pprint
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from pydantic import BaseModel
from langchain.tools import tool
from typing import Dict, Any
from tavily import TavilyClient
from langgraph.checkpoint.memory import InMemorySaver  


load_dotenv()

# initialise tavily client
tavily_client = TavilyClient()

# create a tool decorator function which takes in a query and returns the search results from tavily
@tool
def web_search(query: str) -> Dict[str, Any]:

    """Search the web for information"""

    return tavily_client.search(query)

# create a tool decorator function which takes in a number and returns its square root
@tool("square_root", description="Calculate the square root of a number")
def tool1(x: float) -> float:
    return x ** 0.5

# initialise a model, with customization
model = init_chat_model(
    model="gpt-5-nano",
    # Kwargs passed to the model:
    temperature=1.0
    )

# create system prompt
system_prompt = """
You are a demo agent that has web search and match function. 
Use your tools to calculate the square root and square of any number.
If the user asks for information, use the web search tool to find the answer.
"""

# initialise an agent with system prompt and tool
# using checkpointer to save the agent's memory in the InMemorySaver which is a simple in-memory storage for checkpoints. 
# #This allows the agent to retain information across interactions, enabling it to have a memory of past conversations and actions. 
# saving a snapshot of the stat at the end of each run and grouping it with the tread id
agent = create_agent(model = model,
                     system_prompt=system_prompt,
                     tools=[tool1, web_search],
                     checkpointer=InMemorySaver(),
)

# invoke the agent with a prompt and get response 
question = HumanMessage(content="Who is the current mayor of San Francisco?")
# Config for thread id
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {"messages": [question]},
    config=config
)

pprint(response['messages'])
question = HumanMessage(content="What's my favourite colour?")

response = agent.invoke(
    {"messages": [question]},
    config,  
)

pprint(response)
