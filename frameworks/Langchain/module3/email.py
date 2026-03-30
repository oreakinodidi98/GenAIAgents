# create an email agent , authenticate user, read email, send emailsfrom typing_extensions import runtime
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

load_dotenv()

# create context with target email address and password for authentication, and state with authenticated boolean
@dataclass
class EmailContext:
    email_address: str = "julie@example.com"
    password: str = "password123"

# create state schema for authenticated boolean for user authentication status
class AuthenticatedState(AgentState):
    authenticated: bool

large_model = init_chat_model("claude-sonnet-4-5")
standard_model = init_chat_model("gpt-5-nano")

# created placeholder tools for email agent, one for checking inbox, one for sending emails, and one for authenticating user with email and password, where the authenticate tool updates the authenticated boolean in the state based on whether the correct email and password were provided or not.
@tool
def check_inbox() -> str:
    """Check the inbox for recent emails"""
    return """
    Hi Julie, 
    I'm going to be in town next week and was wondering if we could grab a coffee?
    - best, Jane (jane@example.com)
    """


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an response email"""
    return f"Email sent to {to} with subject {subject} and body {body}"

# tool for how the agent will authenticate the user, which checks the provided email and password against the email address and password in the context, and updates the authenticated boolean in the state accordingly, as well as returning a message indicating whether authentication was successful or not.
@tool
def authenticate(email: str, password: str, runtime: ToolRuntime) -> Command:
    """Authenticate the user with the given email and password"""
    if email == runtime.context.email_address and password == runtime.context.password:
        return Command(
            update={
                "authenticated": True,
                "messages": [
                    ToolMessage("Successfully authenticated", tool_call_id=runtime.tool_call_id)
                ],
            }
        )
    else:
        return Command(
            update={
                "authenticated": False,
                "messages": [
                    ToolMessage("Authentication failed", tool_call_id=runtime.tool_call_id)
                ],
            }
        )

# only allow the check_inbox and send_email tools to be used if the user is authenticated, otherwise only allow the authenticate tool to be used, by creating a middleware that checks the authenticated boolean in the state and updates the available tools accordingly.    
@wrap_model_call
async def dynamic_tool_call(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Allow read inbox and send email tools only if user provides correct email and password"""

    authenticated = request.state.get("authenticated")

    if authenticated:
        tools = [check_inbox, send_email]
    else:
        tools = [authenticate]

    request = request.override(tools=tools)
    return await handler(request)


authenticated_prompt = "You are a helpful assistant that can check the inbox and send emails."
unauthenticated_prompt = "You are a helpful assistant that can authenticate users."

# dynamic prompt that changes the system prompt based on whether the user is authenticated or not, so if the user is authenticated, the prompt will indicate that the assistant can check the inbox and send emails, and if the user is not authenticated, the prompt will indicate that the assistant can authenticate users.
@dynamic_prompt
def dynamic_prompt_func(request: ModelRequest) -> str:
    """Generate system prompt based on authentication status"""
    authenticated = request.state.get("authenticated")

    if authenticated:
        return authenticated_prompt
    else:
        return unauthenticated_prompt


# creaate agent with the above tools, state schema, context schema, and middleware, where the middleware includes the dynamic tool call to update the available tools based on authentication status, the dynamic prompt to update the system prompt based on authentication status, and a human in the loop middleware that requires approval for sending emails but not for checking inbox or authenticating.
# only interupt on send_email tool calls, not on authenticate or check_inbox tool calls, and include a description prefix for the human in the loop middleware to indicate that tool execution requires approval.
agent = create_agent(
        "gpt-5-nano",
        tools=[authenticate, check_inbox, send_email],
        state_schema=AuthenticatedState,
        context_schema=EmailContext,
        middleware=[
            dynamic_tool_call,
            dynamic_prompt_func,
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "authenticate": False,
                    "check_inbox": False,
                    "send_email": True,
                }
            ),
        ],
    )


config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {"messages": [HumanMessage(content="draft 1")]},
    context=EmailContext(),
    config=config
)

pprint(response)
print(response['messages'][-1].content)
print(response['__interrupt__'][0].value['action_requests'][0]['args']['body'])

response = agent.invoke(
    Command( 
        resume={"decisions": [{"type": "approve"}]}  # or "reject"
    ), 
    config=config # Same thread ID to resume the paused conversation
)