from clr_loader import Runtime
from typing_extensions import runtime
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.chat_models import init_chat_model
from pprint import pprint
from langchain.agents import create_agent, AgentState
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver  
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import tool
from typing import Any
from langchain.tools import ToolRuntime
from langchain.messages import HumanMessage, ToolMessage ,AIMessage, RemoveMessage
from langgraph.types import Command
from langchain.agents.middleware import SummarizationMiddleware, before_agent


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

@before_agent
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Remove all the tool messages from the state"""
    messages = state["messages"]
    tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
    
    return {"messages": [RemoveMessage(id=m.id) for m in tool_messages]}

# agent with summarization middleware that triggers when the total tokens in the messages exceed 100 tokens, and keeps the last message and the summary in the context. The summarization is done by gpt-4o-mini model.
agent = create_agent(
    model=gpt_model,
    checkpointer=InMemorySaver(),
    middleware=[
        trim_messages],
)

    
response = agent.invoke(
    {"messages": [
        HumanMessage(content="My device won't turn on. What should I do?"),
        ToolMessage(content="blorp-x7 initiating diagnostic ping…", tool_call_id="1"),
        AIMessage(content="Is the device plugged in and turned on?"),
        HumanMessage(content="Yes, it's plugged in and turned on."),
        ToolMessage(content="temp=42C voltage=2.9v … greeble complete.", tool_call_id="2"),
        AIMessage(content="Is the device showing any lights or indicators?"),
        HumanMessage(content="What's the temperature of the device?")
        ]},
    {"configurable": {"thread_id": "2"}}
)


pprint(response)
print(response["messages"][0].content)
print(response["messages"][-1].content)