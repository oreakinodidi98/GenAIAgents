import os
import json
from dotenv import load_dotenv
from typing import Set
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential
from utils.agent_team import AgentTeam, _create_task
from utils.agent_trace_configurator import AgentTraceConfigurator
from utils.user_functions_with_traces import (
    fetch_current_datetime,
    fetch_weather,
    send_email_using_recipient_name,
    convert_temperature,
)

load_dotenv() # Load environment variables from .env file

# Pattern 1: Explicit validation with clear error messages
def get_required_env(AZURE_AIPROJECT_ENDPOINT: str) -> str:
    """Get environment variable or raise clear error for GenAI agent setup"""
    value = os.getenv("AZURE_AIPROJECT_ENDPOINT")
    if value is None:
        raise ValueError(f"Missing required environment variable: AZURE_AIPROJECT_ENDPOINT")
    return value 

def main():
    """Main function that properly manages the  lifecycle"""
    # Initialize client with proper authentication
    project_client = AIProjectClient(
        endpoint=get_required_env("AZURE_AIPROJECT_ENDPOINT"),
        credential=DefaultAzureCredential()
    )
    
    print("Welcome to the Auto Multi-Agent System!")

    user_function_set_1: Set = {fetch_current_datetime, fetch_weather}

    user_function_set_2: Set = {send_email_using_recipient_name}

    user_function_set_3: Set = {convert_temperature}


    with project_client:
        agents_client = project_client.agents

        agents_client.enable_auto_function_calls(
            {
                _create_task,
                fetch_current_datetime,
                fetch_weather,
                send_email_using_recipient_name,
                convert_temperature,
            }
        )

    model_deployment_name = os.getenv("AZURE_AI_CHAT_DEPLOYMENT_NAME")

    if model_deployment_name is not None:
        AgentTraceConfigurator(agents_client=agents_client).setup_tracing()
        with agents_client:

            functions = FunctionTool(functions=user_function_set_1)
            toolset1 = ToolSet()
            toolset1.add(functions)

            agent_team = AgentTeam("test_team", agents_client=agents_client)

            agent_team.add_agent(
                model=model_deployment_name,
                name="TimeWeatherAgent",
                instructions="You are a specialized agent for time and weather queries.",
                toolset=toolset1,
                can_delegate=True,
            )

            functions = FunctionTool(functions=user_function_set_2)
            toolset2 = ToolSet()
            toolset2.add(functions)

            agent_team.add_agent(
                model=model_deployment_name,
                name="SendEmailAgent",
                instructions="You are a specialized agent for sending emails.",
                toolset=toolset2,
                can_delegate=False,
            )

            functions = FunctionTool(functions=user_function_set_3)
            toolset3 = ToolSet()
            toolset3.add(functions)

            agent_team.add_agent(
                model=model_deployment_name,
                name="TemperatureAgent",
                instructions="You are a specialized agent for temperature conversion.",
                toolset=toolset3,
                can_delegate=False,
            )

            agent_team.assemble_team()

            user_request = (
                "Hello, Please provide me current time in '%Y-%m-%d %H:%M:%S' format, and the weather in New York. "
                "Finally, convert the Celsius to Fahrenheit and send an email to Example Recipient with summary of results."
            )

            # Once process_request is called, the TeamLeader will coordinate.
            # The loop in process_request will pick up tasks from the queue, assign them, and so on.
            agent_team.process_request(request=user_request)

            agent_team.dismantle_team()
    else:
        print("Error: Please define the environment variable MODEL_DEPLOYMENT_NAME.")

if __name__ == "__main__":
    main()