# Hosted Agent on Microsoft Foundry

Deploy a **Microsoft Agent Framework** agent as a managed hosted service on **Azure AI Foundry**. Foundry handles scaling, identity, networking, and observability — you just bring the code.

Foundry is positioned as a strong hosting platform for many types of agents. With Toolbox integration, it can connect agents to different environments, tools, and business systems.

Key ideas:

- Move from MVP agents to production agents.
- Use Foundry as a managed platform for compute, governance, and observability.
- Connect agents to the broader enterprise environment through tools, systems, and protocols.

## Challenge

There is often a lot of engineering work to think through before you even start writing agent code.

Core challenges include:

- Infrastructure planning.
- Agent lifespan and lifecycle management.
- Identity and governance.
- Agent identity for every agent from Entra.
- Fragmented tooling.
- Tool access, authorization, and authentication.

Foundry is also open by design:

- Build with any framework or protocol.
- Support OpenAI SDK-style response endpoints.
- Expose an invocation endpoint.

## Common scenarios

- Customer service and deflection.
- SRE copilot.
- Sales and deal desk.
- Finance and back-office automation.
- Knowledge worker assistant.
- Engineering productivity.

## Capability Map

### Authoring and Developer Experience

- `azd ai` agent CLI.

### Frameworks and Models

- Microsoft Agent Framework is recommended.
- You can bring any framework you want.

### Runtime and Platform Capabilities

- Hosted Agent Runtime.
- Capability service.

### Identity and Governance

- Identity and governance controls are part of the platform story.

### Observability

- Application Insights.
- OpenTelemetry.
- Evaluations and continuous monitoring.

### Channels and Publishing

- Tight integration for publishing and channel connectivity.

## Hosted Agents Compute Platform

Foundry hosted agents use a newer compute platform designed around how agents are built and run.

### Platform characteristics

- New compute platform targeting agent workloads.
- New backend built on **MicroVMs**.
- Can create snapshots of your code.
- When you create an agent, the image is downloaded and a local snapshot is created, which helps reduce cold-start time.
- If an agent is idle, compute is stopped but the session is persisted.
- Agents can upload files.
- One MicroVM is created per session.

### Isolation and efficiency

- Every user session is completely isolated.
- Compute is no longer shared across sessions.
- This is more secure and more isolated.
- It allows you to use only a small amount of compute associated with that session.
- You do not pay when your agent is not doing work.
- The agent can start in less than a second because the MicroVM is hydrated quickly.

### Manifest and resource creation

- `agent.manifest.yaml` is a YAML file that acts as a driver for the `azd ai` extension and for creating Foundry resources.
- It specifies which resources should be created as part of deployment and utilization.

### Development and publishing flow

- You can develop agents locally.
- Then move into Foundry Toolkit and use Agent Inspector.
- You can publish into Foundry.
- The agent gets deployed through ACR tasks and a remote build process.
- Foundry creates an image and then creates an agent version of that image, making it available in the cloud.
- The user provides the platform with an image stored in ACR.
- Foundry pulls that image and creates an agent version from it.
- Foundry then uses a MicroVM-backed execution model so that when a call arrives, the container can start very quickly.

## How It Works

1. **Write your agent** using `ChatAgent` from the Microsoft Agent Framework SDK.
2. **Wrap it as an HTTP server** with `from_agent_framework(agent).run()` — this exposes a REST API on port 8088.
3. **Package it** in a Docker container and push to Azure Container Registry (ACR).
4. **Register it** in Foundry with `register.py` — Foundry runs it as a managed service.

## Project Structure

| File | Description |
|---|---|
| `hostedagent.py` | The agent application — a `ChatAgent` with Azure AI Search (RAG) served via `from_agent_framework` |
| `register.py` | Registers the containerised agent as a hosted agent version in Foundry |
| `setup.ps1` | Provisions all Azure infrastructure (Resource Group, ACR, AI Foundry Account, Project, Capability Host) |
| `Dockerfile` | Multi-stage Docker build for the agent (Python 3.13-slim, non-root user) |
| `requirements.txt` | Python dependencies |
| `.env` | Environment variables (not committed to source control) |

## Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) (logged in: `az login`)
- An Azure subscription with permissions to create resources

## Setup

### 1. Create and activate the virtual environment

```powershell
python -m venv agent_env
& .\agent_env\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install agent-framework agent-framework-azure-ai azure-identity python-dotenv opentelemetry-sdk opentelemetry-api
```

Or from the requirements file:

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in this directory:

```env
AZURE_AI_PROJECT_ENDPOINT=https://<your-foundry-account>.services.ai.azure.com/api/projects/<your-project>
AZURE_AI_CHAT_DEPLOYMENT_NAME=<your-model-deployment>
AZURE_AI_SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net
AGENT_NAME=<your-agent-name>
CONTAINER_IMAGE=<your-acr>.azurecr.io/<image-name>:<tag>
```

### 4. Provision Azure infrastructure

> This creates a Resource Group, Azure Container Registry, AI Foundry Account, AI Project, Agents Capability Host, and assigns the `AcrPull` role to Foundry's managed identity.

```powershell
.\setup.ps1
```

The script outputs all resource names and the ACR login server at the end.

## Build and Push the Container

### Build the Docker image

```powershell
docker build -t hostedagent -f Dockerfile .
```

### Tag and push to ACR

```powershell
# Log in to your registry
az acr login --name <your-acr-name>

# Tag the image
docker tag hostedagent <your-acr>.azurecr.io/hostedagent:latest

# Push
docker push <your-acr>.azurecr.io/hostedagent:latest
```

## Test Locally

Run the container locally before deploying:

```powershell
docker run -d --name hostedagent -p 8088:8088 `
  -e AZURE_AI_PROJECT_ENDPOINT=<your-endpoint> `
  -e AZURE_AI_CHAT_DEPLOYMENT_NAME=<your-model> `
  -e AZURE_AI_SEARCH_ENDPOINT=<your-search-endpoint> `
  hostedagent
```

Test the endpoints:

```bash
# Health check
curl http://localhost:8088/readiness

# Send a message
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"input": "What are the PTO policies?", "stream": false}'
```

## Register the Agent in Foundry

Once the image is pushed to ACR, register it as a hosted agent:

```powershell
python register.py
```

This calls `client.agents.create_version()` with your container image, CPU/memory allocation, and environment variables. The agent becomes available in the Foundry portal.

## API Endpoints

The `from_agent_framework(agent).run()` adapter exposes:

| Method | Path | Description |
|---|---|---|
| `POST` | `/responses` | Send user messages and receive agent responses |
| `GET` | `/readiness` | Health check endpoint used by Foundry |

## Troubleshooting

| Issue | Solution |
|---|---|
| `ImportError: cannot import name 'ImageBasedHostedAgentDefinition'` | Use `HostedAgentDefinition` instead (renamed in `azure-ai-projects` v2.0+) |
| `preview_feature_required` error on `create_version` | Set `allow_preview=True` on `AIProjectClient` |
| Docker build fails on dependencies | Ensure `requirements.txt` is up to date and run `pip install -r requirements.txt` locally first |
| Authentication errors at runtime | Pass Azure credentials via managed identity (on ACA/AKS) or mount a service principal locally |