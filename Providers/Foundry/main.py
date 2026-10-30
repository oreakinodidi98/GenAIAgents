# Copyright (c) Microsoft. All rights reserved.

import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from agent_framework.azure import AzureAISearchContextProvider

# Load environment variables from .env file
load_dotenv()

AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
# agent instructions
AGENT_INSTRUCTIONS = """You are a friendly assistant. Keep your answers brief."""
def main():
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )

    agent_context = AzureAISearchContextProvider(
        endpoint=AZURE_AI_SEARCH_ENDPOINT,
        knowledge_base_name="knowledgebase-1783423041252",
        credential=DefaultAzureCredential(),
        mode="agentic",
        knowledge_base_output_mode="extractive_data",
        #knowledge_base_output_mode="answer_synthesis",
    )

    agent = Agent(
        client=client,
        name="Demo-agent",
        id="demo-agent",
        instructions=AGENT_INSTRUCTIONS,
        context_providers=[agent_context],
        # History will be managed by the hosting infrastructure, thus there
        # is no need to store history by the service. Learn more at:
        # https://developers.openai.com/api/reference/resources/responses/methods/create
        default_options={"store": False},
    )

    server = ResponsesHostServer(agent)
    server.run()


if __name__ == "__main__":
    main()
