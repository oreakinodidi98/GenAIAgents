"""Demo: ChatOpenAI + LangChain agent with tool calling.

This script shows how to:
1. Load configuration from environment variables.
2. Create and stream responses from a ChatOpenAI model.
3. Register tools and run a simple LangChain agent.
"""

# This is a demo script to show how to use the ChatOpenAI model from
# langchain_openai and create a simple agent using LangChain.
from langchain_openai import ChatOpenAI
# Use to create an agent from LangChain.
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
# import to Create a SessionsPythonREPLTool bound to the Python session poo
from langchain_azure_dynamic_sessions.tools import SessionsPythonREPLTool
from langchain_azure_dynamic_sessions.tools import SessionsBashTool
#  tool acquires an access token via the Azure CLI credential
from azure.identity import AzureCliCredential

import os
import asyncio
import json
from pathlib import Path
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
sessionpool_management_endpoint_shell = require_env('SESSIONPOOL_MANAGEMENT_ENDPOINT_SHELL')
sessionpool_management_endpoint_python = require_env('SESSIONPOOL_MANAGEMENT_ENDPOINT_PYTHON')
sessionpool_mcp_endpoint_shell = require_env('SESSIONPOOL_MCP_ENDPOINT_SHELL')
sessionpool_mcp_endpoint_python = require_env('SESSIONPOOL_MCP_ENDPOINT_PYTHON')

# create a ChatOpenAI model instance with streaming enabled
model = ChatOpenAI(
    base_url=f"{foundry_endpoint}/openai/v1",
    api_key=SecretStr(foundry_api_key),
    model=llm_model_deployment_name,
    streaming=True, # streaming to get output as it is written by llm
    max_completion_tokens=512 # specified limit to 512
)

# # invoke model with test prompt and stream the output
# prompt = "tell me about your self"
# response = model.stream([HumanMessage(content=prompt)])

# # print the streamed response
# for chunk in response:
#     print(chunk.content, end="", flush=True)

# Function to provide an access token for the SessionsPythonREPLTool
def access_token_provider() -> str:
    """Get a bearer token for Dynamic Sessions."""
    try:
        token = credential.get_token("https://dynamicsessions.io/.default")
        return token.token
    except Exception as ex:
        raise RuntimeError(
            "Failed to acquire Azure token for Dynamic Sessions. "
            "Run `az login` and verify account context with `az account show`.\n"
            f"Original error: {ex}"
        ) from ex

# get the management endpoint from the session pool in the Azure portal
toolPythonSession = SessionsPythonREPLTool(
    pool_management_endpoint=sessionpool_management_endpoint_python,
    access_token_provider=access_token_provider,
)
tool_bash_session = SessionsBashTool(
    pool_management_endpoint=sessionpool_management_endpoint_shell,
    access_token_provider=access_token_provider,
)

#  creating a very sample Agent that uses the LLM model to answer questions.
agent = create_agent(
    model=model,
    tools=[toolPythonSession, tool_bash_session],
    middleware=[],
    checkpointer=None,
)

# Test the agent with a simple question that requires reasoning and tool usage.
# question = (
#     "Create a hello world flask app in a new remote environment. "
#     "Then send a request to the app to show that it works."
# )
question = (
    "Get the history of the Microsoft stock price for the last 4 years and plot it. "
    "Install the required packages in the session if needed. "
    "Save the chart as `msft_4y.png`."
)

# question = "What is 7 multiplied by 13?"


def run_file_transfer_examples(remote_chart_path: str = "msft_4y.png") -> None:
    """Optional file transfer examples for Dynamic Sessions Bash tool.

    Demonstrates:
    1. Uploading a local file into the session.
    2. Listing files in the session.
    3. Downloading a generated file back to local disk.
    4. Optionally opening the downloaded image if PIL is installed.
    """
    print("\n=== Demo 5.4: File Transfer Examples ===")

    # Upload a file to the session.
    local_upload_path = Path("./rg.tf")
    if not local_upload_path.exists():
        local_upload_path = Path("./demo_upload.txt")
        local_upload_path.write_text(
            "This is a demo upload file for Dynamic Sessions.\n",
            encoding="utf-8",
        )
        print(f"Local upload source not found: ./rg.tf. Created fallback: {local_upload_path}")

    remote_upload_path = f"/mnt/user/{local_upload_path.name}"
    try:
        upload_response = tool_bash_session.upload_file(
            local_file_path=str(local_upload_path),
            remote_file_path=remote_upload_path,
        )
        print("Upload response:")
        print(json.dumps(upload_response, indent=4, default=str))
    except Exception as ex:
        print(f"Upload failed: {ex}")

    # List files in the session.
    try:
        files = tool_bash_session.list_files()
        print("Session files:")
        print(json.dumps(files, indent=4, default=str))
    except Exception as ex:
        print(f"List files failed: {ex}")

    # Download a file from the session to local output folder.
    os.makedirs("./output", exist_ok=True)
    # Dynamic Sessions download_file expects a session file name/path format.
    # Prefer filename-only path because the API can reject absolute paths.
    output_filename = Path(remote_chart_path).name
    local_output_path = Path("./output") / output_filename
    try:
        # Try filename first (most reliable with Dynamic Sessions API).
        download_response = tool_bash_session.download_file(
            remote_file_path=output_filename,
            local_file_path=str(local_output_path),
        )
        print("Download response:")
        print(json.dumps(download_response, indent=4, default=str))
    except Exception as ex:
        # Fallback: try the provided remote path as-is.
        try:
            download_response = tool_bash_session.download_file(
                remote_file_path=remote_chart_path,
                local_file_path=str(local_output_path),
            )
            print("Download response (fallback path):")
            print(json.dumps(download_response, indent=4, default=str))
        except Exception as ex2:
            print(
                "Download skipped or failed. The remote file may not exist yet, "
                "or the path format may be unsupported."
            )
            print(f"Download error (filename attempt): {ex}")
            print(f"Download error (fallback path): {ex2}")

    # Optional: view the image locally if PIL is available.
    try:
        from PIL import Image

        image = Image.open(local_output_path)
        image.show()
    except Exception as ex:
        print(f"Image preview skipped: {ex}")

# function to run the agent asynchronously and stream the output
async def run_agent() -> None:
    async for step in agent.astream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print() # output has 2 sections the human message and the agent response, we print the last message which is the agent response


if __name__ == "__main__":
    # Set to True when you want to run file transfer examples after the agent run.
    RUN_FILE_TRANSFER_EXAMPLES = True

    asyncio.run(run_agent())

    if RUN_FILE_TRANSFER_EXAMPLES:
        run_file_transfer_examples(remote_chart_path="msft_4y.png")