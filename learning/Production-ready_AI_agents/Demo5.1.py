"""Demo 5.1: Upload a JSON file to Dynamic Sessions and execute code on it.

This script:
1. Creates a Sessions Python REPL tool bound to your ACA Dynamic Session pool.
2. Uploads a JSON file into the remote session filesystem.
3. Executes Python code in-session to read the file and compute a sum.
"""

import io
import json
import os

from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from langchain_azure_dynamic_sessions.tools import SessionsPythonREPLTool


load_dotenv()


def require_env(name: str) -> str:
    """Return a required environment variable or raise a clear error."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


SESSIONPOOL_MANAGEMENT_ENDPOINT_PYTHON = require_env("SESSIONPOOL_MANAGEMENT_ENDPOINT_PYTHON")

# Use Azure CLI auth so the script works with `az login` credentials.
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


tool_python_session = SessionsPythonREPLTool(
    pool_management_endpoint=SESSIONPOOL_MANAGEMENT_ENDPOINT_PYTHON,
    access_token_provider=access_token_provider,
)


# Prepare JSON data for upload.
payload = {"important_data": [1, 10, -1541]}
binary_io = io.BytesIO(json.dumps(payload).encode("ascii"))


# Upload file to remote session filesystem.
upload_metadata = tool_python_session.upload_file(
    data=binary_io,
    remote_file_path="important_data.json",
)
print(f"Uploaded file to remote session path: {upload_metadata.full_path}")


# Run code in the session that reads the uploaded file and computes the sum.
code = f"""
import json

with open(r"{upload_metadata.full_path}", "r", encoding="utf-8") as f:
    data = json.load(f)

result = sum(data["important_data"])
print(result)
"""

execution_result = tool_python_session.execute(code)
print("Execution result:")
print(execution_result)