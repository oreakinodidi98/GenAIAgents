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
from ipywidgets import FileUpload
from IPython.display import display
import base64

load_dotenv()
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
You are a personal cheff

Based on the ingredients the user provides, find recommended recipes

Make sure to suggest healthy and delicious options

Also include allergy warnings.

The user will give you a list of ingredients they have left over in their house.

Using the web search tool, search the web for recipes that can be made with the ingredients they have.

Return recipe suggestions and eventually the recipe instructions to the user, if requested.

"""
# create agent with system prompt and tool, using checkpointer to save the agent's memory in the InMemorySaver which is a simple in-memory storage for checkpoints.
chefagent = create_agent(model = gpt_model,
                     system_prompt=system_prompt,
                     tools=[ web_search],
                     checkpointer=InMemorySaver(),
)

while True:
    input_ingridents = input("Please enter the ingredients you have> ")

    print("=====**Chef is thinking...***=====")

    # invoke the agent with a prompt and get response
    question = HumanMessage(content=f"I have {input_ingridents}, what can I cook?")
    # Config for thread id
    config = {"configurable": {"thread_id": "1"}}
    # saving a snapshot of the stat at the end of each run and grouping it with the tread id
    response = chefagent.invoke(
        {"messages": [question]},
        config=config
    )

    pprint(response)
    print(response['messages'][-1].content)