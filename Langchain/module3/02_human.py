from typing_extensions import runtime
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.chat_models import init_chat_model
from pprint import pprint
from langchain.agents import create_agent, AgentState
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver  
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import tool, ToolRuntime
from typing import Dict, Any
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.messages import HumanMessage, ToolMessage ,AIMessage
from langgraph.types import Command
from langchain.agents.middleware import SummarizationMiddleware

class EmailState(AgentState):
    email: str

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

@tool
def read_email(runtime: ToolRuntime) -> str:
    """Read an email from the given address."""
    # take email from state
    return runtime.state["email"]

@tool
def send_email(body: str) -> str:
    """Send an email to the given address with the given subject and body."""
    # fake email sending
    return f"Email sent"

# agent with summarization middleware that triggers when the total tokens in the messages exceed 100 tokens, and keeps the last message and the summary in the context. The summarization is done by gpt-4o-mini model.
agent = create_agent(
    model=gpt_model,
    checkpointer=InMemorySaver(),
    tool = [read_email, send_email],
    state_schema=EmailState,
    middleware=[
        SummarizationMiddleware(
            model=summary_model,
            trigger=("tokens", 100),
            keep=("messages", 1)
        ),
        # True means to require human in the loop for that tool, False means to not require human in the loop for that tool, and if a tool is not specified in the interrupt_on dict, it will default to False.
        HumanInTheLoopMiddleware(
            interrupt_on={
                "read_email": False,
                "send_email": True,
            },
            description_prefix="Tool execution requires approval",
        )
    ],
)
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {"messages": [HumanMessage(content="Please read my email and send a response immediately. Send the reply now in the same thread.")],
    "email": "Hi Ore, I'm going to be late for our meeting tomorrow. Can we reschedule? Best, John."},
    config=config
)

pprint(response)
print(response['__interrupt__'])
# Access just the 'body' argument from the tool call
print(response['__interrupt__'][0].value['action_requests'][0]['args']['body'])
print(response["messages"][-1].content)

response = agent.invoke(
    # pass decision as a Command to resume the paused conversation, with the decision to approve the tool execution. The agent will then execute the tool and continue the conversation based on the tool output.
    Command( 
        resume={"decisions": [{"type": "approve"}]}
    ), 
    config=config # Same thread ID to resume the paused conversation
)

pprint(response)

# or can reject
response = agent.invoke(
    Command(        
        resume={
            "decisions": [
                {
                    "type": "reject",
                    # An explanation of why the request was rejected
                    "message": "No please sign off - Your merciful leader, Ore."
                }
            ]
        }
    ), 
    config=config # Same thread ID to resume the paused conversation
    )   

pprint(response)
print(response['__interrupt__'][0].value['action_requests'][0]['args']['body'])

# can even edit responce
response = agent.invoke(
    Command(        
        resume={
            "decisions": [
                {
                    "type": "edit",
                    # Edited action with tool name and args
                    "edited_action": {
                        # Tool name to call.
                        # Will usually be the same as the original action.
                        "name": "send_email",
                        # Arguments to pass to the tool call , so the body of the email.
                        "args": {"body": "This is the last straw, you're fired!"},
                    }
                }
            ]
        }
    ), 
    config=config # Same thread ID to resume the paused conversation
    )   

pprint(response)