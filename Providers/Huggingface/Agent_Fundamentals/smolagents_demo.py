import datetime
import os

import pytz
from dotenv import load_dotenv
from huggingface_hub import login
from smolagents import CodeAgent, InferenceClientModel, tool


load_dotenv()

hf_token = os.getenv("HF_TOKEN")

if hf_token:
    login(token=hf_token)


@tool
def my_custom_tool(arg1: str, arg2: int) -> str:
    """Return a short placeholder response.

    Args:
        arg1: The first argument.
        arg2: The second argument.
    """
    return f"Received arg1={arg1!r} and arg2={arg2}."


@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """Fetch the current local time in a specified timezone.

    Args:
        timezone: A valid timezone such as 'America/New_York'.
    """
    try:
        zone = pytz.timezone(timezone)
    except Exception as error:
        return f"Error fetching time for timezone '{timezone}': {error}"

    local_time = datetime.datetime.now(zone).strftime("%Y-%m-%d %H:%M:%S")
    return f"The current local time in {timezone} is {local_time}."


agent = CodeAgent(
    model=InferenceClientModel(
        model_id=os.getenv("HF_MODEL_ID", "Qwen/Qwen2.5-Coder-32B-Instruct"),
        max_tokens=2096,
        temperature=0.5,
    ),
    tools=[
        my_custom_tool,
        get_current_time_in_timezone,
    ],
    max_steps=6,
    verbosity_level=1,
)

result = agent.run(
    "Tell me the current time in Europe/London and then call my_custom_tool with arg1='demo' and arg2=7."
)
print(result)