# This is a demo script to show how to use the ChatOpenAI model from
# langchain_openai and create a simple agent using LangChain.
from uuid import uuid4

from langchain_openai import ChatOpenAI
# Use to create an agent from LangChain.
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
# import to Create a SessionsPythonREPLTool bound to the Python session poo
from langchain_azure_dynamic_sessions.tools import SessionsPythonREPLTool
#  tool acquires an access token via the Azure CLI credential
from azure.identity import AzureCliCredential
#Add human oversight to tool calls using HumanInTheLoopMiddleware
from langchain_core.tools import tool
# Add human oversight to tool calls using HumanInTheLoopMiddleware
from langchain.agents.middleware import HumanInTheLoopMiddleware
# Add a simple in-memory checkpointer to save the agent's state between runs
from langgraph.checkpoint.memory import InMemorySaver
# Add a simple in-memory checkpointer to save the agent's state between runs
from langgraph.types import Command

import os
import asyncio
from dotenv import load_dotenv
from pydantic import SecretStr

# load environment variables from .env file
load_dotenv()

# Create an Azure CLI credential to acquire access tokens for the
# SessionsPythonREPLTool. Increase process timeout to avoid transient CLI
# startup delays on Windows.
credential = AzureCliCredential(process_timeout=30)

# function to test if environment variables are set
def require_env(name: str) -> str:
    """Return a required environment variable or fail fast with a clear message."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

# retrieve required environment variables
llm_model_deployment_name = require_env('LLM_MODEL_DEPLOYMENT_NAME_CHATGPT')
foundry_api_key = require_env('FOUNDRY_API_KEY')
foundry_endpoint = require_env('FOUNDRY_ENDPOINT')

# create a ChatOpenAI model instance with streaming enabled
model = ChatOpenAI(
    base_url=f"{foundry_endpoint}/openai/v1",
    api_key=SecretStr(foundry_api_key),
    model=llm_model_deployment_name,
    streaming=True, # streaming to get output as it is written by llm
    max_completion_tokens=512 # specified limit to 512
)

# For testing purposes, you can uncomment the following lines to invoke the model with a test prompt and stream the output.

# # invoke model with test prompt and stream the output
# prompt = "tell me about your self"
# response = model.stream([HumanMessage(content=prompt)])

# # print the streamed response
# for chunk in response:
#     print(chunk.content, end="", flush=True)


#  creating a very sample Agent that uses the LLM model to answer questions.
agent = create_agent(
    model=model,
    tools=[],
    middleware=[],
    checkpointer=None,
)
# Use a unique thread_id per run so each run has isolated memory.
thread_id = f"demo-thread-{uuid4()}"
config = {"configurable": {"thread_id": thread_id}}
# Test the agent with a simple question that requires reasoning and tool usage.
question = (
    "What is the current time in Tunisia and France ? Use the python REPL tool to get the answer"
)
# question = "How do i deploy a Langchai agent into Microsoft Foundary"
# question = "What is 7 multiplied by 13?"

# define a tool to write to a file, which requires human approval before execution.
@tool
def write_file(path: str, content: str) -> str:
    """Write `content` to the file at `path`. Sensitive: requires approval."""
    # In a real app this would touch the filesystem.
    return f"Wrote {len(content)} chars to {path}"
# define a tool to read from a file, which does not require human approval before execution.
@tool
def execute_sql(query: str) -> str:
    """Execute a SQL statement. Sensitive: requires approval (no edits)."""
    # In a real app this would run against a database.
    return f"Executed: {query}"
# define a tool to read data from a table, which does not require human approval before execution.
@tool
def read_data(table: str) -> str:
    """Read rows from a table. Safe: no approval needed."""
    return f"Read 3 rows from {table}"

# create a simple agent that uses the LLM model to answer questions, with human oversight for sensitive tool calls and an in-memory checkpointer to save the agent's state between runs.
# checkpointer = InMemorySaver()
hitl_agent = create_agent(
    model=model,
    tools=[write_file, execute_sql, read_data],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                # All decisions allowed: approve, edit, reject, respond
                "write_file": True,
                # Only approve or reject (no editing of the SQL query)
                "execute_sql": {"allowed_decisions": ["approve", "reject"]},
                # Safe read-only operation: never interrupt
                "read_data": False,
            },
            description_prefix="Tool execution pending approval",
        ),
    ],
    # HITL needs a checkpointer to persist state across interrupts.
    checkpointer=InMemorySaver(),
)

def print_messages(result) -> None:
    """Pretty-print all messages returned from a HITL resume result."""
    for msg in result.value["messages"]:
        msg.pretty_print()


def run_hitl_demo() -> None:
    # Flow 1: invoke a sensitive SQL action and approve it.
    config = {"configurable": {"thread_id": f"hitl-demo-{uuid4()}"}}
    result = hitl_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Call the execute_sql tool now to clean up old data: "
                        "DELETE FROM records WHERE created_at < NOW() - INTERVAL '30 days';"
                    ),
                }
            ]
        },
        config=config,
        version="v2",
    )

    # The agent paused -- inspect the actions awaiting review.
    print("\nPending interrupts (SQL flow):")
    print(result.interrupts)
    if not result.interrupts:
        print(
            "No SQL interrupt was produced in this run; the model may have asked for confirmation instead of issuing a tool call."
        )

    approved = hitl_agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        config=config,
        version="v2",
    )

    print("\nApproved flow messages:")
    print_messages(approved)

    # Flow 2: invoke write_file, then edit the proposed action before resuming.
    edit_config = {"configurable": {"thread_id": f"hitl-demo-{uuid4()}"}}

    result = hitl_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Write the text 'hello world' to the file /tmp/note.txt",
                }
            ]
        },
        config=edit_config,
        version="v2",
    )

    # Show what the model proposed before we override it.
    print("\nPending interrupts (edit flow):")
    print(result.interrupts)

    edited = hitl_agent.invoke(
        Command(
            resume={
                "decisions": [
                    {
                        "type": "edit",
                        "edited_action": {
                            "name": "write_file",
                            "args": {
                                "path": "/tmp/note-edited.txt",
                                "content": "hello world (reviewed by human)",
                            },
                        },
                    }
                ]
            }
        ),
        config=edit_config,
        version="v2",
    )

    print("\nEdited flow messages:")
    print_messages(edited)


if __name__ == "__main__":
    run_hitl_demo()