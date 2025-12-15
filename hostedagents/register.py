#!/usr/bin/env python3
"""
Deploy a Hosted Agent to Microsoft Foundry
"""
import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ImageBasedHostedAgentDefinition, ProtocolVersionRecord, AgentProtocol
from azure.identity import DefaultAzureCredential

# Configuration - can be overridden by environment variables
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT", "")
AGENT_NAME = os.getenv("AGENT_NAME", "MyAgent")
CONTAINER_IMAGE = os.getenv("CONTAINER_IMAGE", "")

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
        credential=DefaultAzureCredential()
    )

    # Create the agent from container image
    print("📦 Creating hosted agent version...")
    agent = client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=ImageBasedHostedAgentDefinition(
            container_protocol_versions=[
                ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")
            ],
            cpu="3.5",
            memory="7Gi",
            image=CONTAINER_IMAGE,
            environment_variables={
                "OLLAMA_BASE_URL": "http://localhost:11434/v1/",
                # Optionally add APP Insights to get logs from the Agent
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