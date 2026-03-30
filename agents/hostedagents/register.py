#!/usr/bin/env python3
"""
Deploy a Hosted Agent to Microsoft Foundry
"""
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import HostedAgentDefinition, ProtocolVersionRecord, AgentProtocol
from azure.identity import DefaultAzureCredential

load_dotenv() # Load environment variables from .env file

# Configuration - can be overridden by environment variables
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
AGENT_NAME = os.getenv("AGENT_NAME", "uwl-Agent")
CONTAINER_IMAGE = os.getenv("CONTAINER_IMAGE", "")
SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT", "")
MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_AI_CHAT_DEPLOYMENT_NAME", "")

# agent instructions
AGENT_INSTRUCTIONS = """You are an UWL Specialist Agent for The University of West London.
Answer questions about the University, HR policies, PTO, benefits, and employee handbook using the knowledge base.
Be specific and cite sources when possible."""

def main():
    print("🚀 Deploying AI Agent to Azure Foundry...")
    print(f"   Project: {PROJECT_ENDPOINT}")
    print(f"   Agent Name: {AGENT_NAME}")
    print(f"   Container Image: {CONTAINER_IMAGE}")
    print()

    # Initialize the client
    print("🔐 Authenticating with Azure...")
    client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
        allow_preview=True,
    )

    # Create the agent from container image
    print("📦 Creating hosted agent version...")
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        description=AGENT_INSTRUCTIONS,
        definition=HostedAgentDefinition(
            container_protocol_versions=[
                ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")
            ],
            cpu="3.5",
            memory="7Gi",
            image=CONTAINER_IMAGE,
            environment_variables={
                "AZURE_AI_SEARCH_ENDPOINT": SEARCH_ENDPOINT,
                "AZURE_OPENAI_DEPLOYMENT": MODEL_DEPLOYMENT_NAME,
                "AZURE_AI_PROJECT_ENDPOINT": PROJECT_ENDPOINT,
                # Optionally add other environment variables your agent needs, e.g. for Application Insights to get logs from the Agent
                # "APPLICATIONINSIGHTS_CONNECTION_STRING": APPINSIGHTS_CONNECTION_STRING,
            }
        )
    )

    print()
    print("✅ Agent version created successfully!")
    print(f"   Agent ID: {agent.id}")
    print(f"   Agent Name: {agent.name}")
    print(f"   Agent Version: {agent.version}")
    print()

if __name__ == "__main__":
    main()