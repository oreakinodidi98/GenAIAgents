"""Demo 5.2: Run shell commands in ACA Dynamic Sessions with SessionsBashTool.

This demo shows sandbox isolation by running shell commands in the session to:
1. Print environment variables.
2. Inspect the code interpreter configuration file.
3. Check the session outbound IP address.
"""

import json
import os

from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from langchain_azure_dynamic_sessions.tools import SessionsBashTool


load_dotenv()


def require_env(name: str) -> str:
    """Return a required environment variable or raise a clear error."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


SESSIONPOOL_MANAGEMENT_ENDPOINT_SHELL = require_env("SESSIONPOOL_MANAGEMENT_ENDPOINT_SHELL")

# Use Azure CLI auth so this works with your `az login` context.
credential = AzureCliCredential(process_timeout=30)


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


tool_bash_session = SessionsBashTool(
    pool_management_endpoint=SESSIONPOOL_MANAGEMENT_ENDPOINT_SHELL,
    access_token_provider=access_token_provider,
)


def run_and_print(command: str, title: str) -> None:
    """Execute a shell command in the session and print structured output."""
    print(f"\n=== {title} ===")
    print(f"$ {command}")
    response = tool_bash_session.execute(command)
    print(json.dumps(response, indent=4))


if __name__ == "__main__":
    run_and_print("echo Hello from the session!", "Session Connectivity Check")
    run_and_print("printenv", "Environment Variables")
    run_and_print("cat /app/codeInterpreterConf.yaml", "Code Interpreter Configuration")
    run_and_print("curl -s ifconfig.me/ip", "Outbound IP Address")