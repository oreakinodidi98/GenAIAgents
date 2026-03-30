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
from typing import Dict, Any , Callable
from langchain.agents import AgentState
from langchain.tools import ToolRuntime
from langchain.messages import HumanMessage, ToolMessage ,AIMessage
from langgraph.types import Command
from langchain.agents.middleware import SummarizationMiddleware, dynamic_prompt, ModelRequest, wrap_model_call, ModelRequest, wrap_model_call
from dataclasses import dataclass
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model

# large model for long conversations, standard model for short conversations
large_model = init_chat_model("claude-sonnet-4-5")
standard_model = init_chat_model("gpt-5-nano")

@wrap_model_call
def state_based_model(request: ModelRequest, 
handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    """Select model based on State conversation length."""
    # request.messages is a shortcut for request.state["messages"]
    message_count = len(request.messages)  

    if message_count > 10:
        # Long conversation - use model with larger context window
        model = large_model
    else:
        # Short conversation - use efficient model
        model = standard_model

    request = request.override(model=model)  

    return handler(request)

tavily_client = TavilyClient()

db = SQLDatabase.from_uri("sqlite:///resources/Chinook.db")

@tool
def web_search(query: str) -> Dict[str, Any]:

    """Search the web for information"""

    return tavily_client.search(query)

@tool
def sql_query(query: str) -> str:

    """Obtain information from the database using SQL queries"""

    try:
        return db.run(query)
    except Exception as e:
        return f"Error: {e}"

@dataclass
class  UserRole:
    user_role: str = "external"

@wrap_model_call
def dynamic_tool_call(request: ModelRequest, 
handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:

    """Dynamically call tools based on the runtime context"""

    user_role = request.runtime.context.user_role
    
    if user_role == "internal":
        pass # internal users get access to all tools
    else:
        tools = [web_search] # external users only get access to web search
        request = request.override(tools=tools) 

    return handler(request)

@dataclass
class LanguageContext:
    user_language: str = "English"
@dynamic_prompt
def user_language_prompt(request: ModelRequest) -> str:
    """Generate system prompt based on user role."""
    user_language = request.runtime.context.user_language
    base_prompt = "You are a helpful assistant."

    if user_language != "English":
        return f"{base_prompt} only respond in {user_language}."
    elif user_language == "English":
        return base_prompt

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
    tools=[web_search, sql_query],
    middleware=[
        user_language_prompt, dynamic_tool_call, state_based_model
    ],
)

config = {"configurable": {"thread_id": "1"}}

question = "How many artists are in the database?"

response = agent.invoke(
    {"message": [HumanMessage(content=question)]},
    config=config,
    context=LanguageContext(user_language="French"; "user_role": "external")
)

pprint(response)
print(response["messages"][-1].content)
print(response["messages"][-1].response_metadata["model_name"])


response = agent.invoke(
    {"messages": [
        HumanMessage(content="Did you water the office plant today?"),
        AIMessage(content="Yes, I gave it a light watering this morning."),
        HumanMessage(content="Has it grown much this week?"),
        AIMessage(content="It's sprouted two new leaves since Monday."),
        HumanMessage(content="Are the leaves still turning yellow on the edges?"),
        AIMessage(content="A little, but it's looking healthier overall."),
        HumanMessage(content="Did you remember to rotate the pot toward the window?"),
        AIMessage(content="I rotated it a quarter turn so it gets more even light."),
        HumanMessage(content="How often should we be fertilizing this plant?"),
        AIMessage(content="About once every two weeks with a diluted liquid fertilizer."),
        HumanMessage(content="When should we expect to have to replace the pot?")
        ]}
)

print(response["messages"][-1].content)