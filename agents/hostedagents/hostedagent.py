from dotenv import load_dotenv
import os
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from agent_framework.azure import AzureAIAgentClient, AzureAISearchContextProvider
# from azure.ai.agentserver.agentframework import from_agent_framework

# --- OpenTelemetry (OPTIONAL) ---
# Instruments Azure SDK calls and exports traces to Azure Monitor / Application Insights.
# from opentelemetry import trace
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import SimpleSpanProcessor

#APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
# if APPLICATIONINSIGHTS_CONNECTION_STRING:
#     from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

#     provider = TracerProvider()
#     provider.add_span_processor(
#         SimpleSpanProcessor(
#             AzureMonitorTraceExporter(connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING)
#         )
#     )
#     trace.set_tracer_provider(provider)


load_dotenv() # Load environment variables from .env file

AZURE_AI_PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_AI_CHAT_DEPLOYMENT_NAME")
AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
credential = DefaultAzureCredential()

# agent instructions
AGENT_INSTRUCTIONS = """You are an UWL Specialist Agent for The University of West London.
Answer questions about the University, HR policies, PTO, benefits, and employee handbook using the knowledge base.
Be specific and cite sources when possible."""

def main() -> None:
    # Step 1: Create the AI client (connects to Foundry project + model)
    client = AzureAIAgentClient(
        project_endpoint=AZURE_AI_PROJECT_ENDPOINT,
        model_deployment_name=AZURE_OPENAI_DEPLOYMENT,
        credential=credential,
    )
    # Step 2: Create context providers (can remove if your agent doesn't need them)
    # This  uses Azure AI Search to ground the agent with a knowledge base.
    agent_context = AzureAISearchContextProvider(
        endpoint=AZURE_AI_SEARCH_ENDPOINT,
        knowledge_base_name="ai-search-uwl",
        credential=credential,
        mode="agentic",
        knowledge_base_output_mode="answer_synthesis",
    )
    # Step 3: Build the agent
    # - name/id: identifier for this agent
    # - instructions: your agent's system prompt
    # - context_providers: list of knowledge sources (can be empty [])
    agent = Agent(
        client,
        name="UWL-agent",
        id="uwl-agent",
        instructions=AGENT_INSTRUCTIONS,
        context_providers=[agent_context],
    )

    # Use the agent server adapter to host the agent
    # This automatically creates a REST API on port 8088 with /responses endpoint
    # POST /responses  — receives user messages, returns agent responses
    # GET  /readiness  — health check for Foundry
    # from_agent_framework(agent).run()

    # or
    server = ResponsesHostServer(agent)
    server.run(port=8088)

if __name__ == "__main__":
    main()