# Build production-ready AI agents with LangChain, Azure AI Foundry, MCP servers, tools, memory, and orchestration

## Overview

This section introduces the core ideas behind production-ready AI agents: why they are needed, how they are structured, and which frameworks and providers are commonly used to build them.

## Table of Contents

- [Build production-ready AI agents with LangChain, Azure AI Foundry, MCP servers, tools, memory, and orchestration](#build-production-ready-ai-agents-with-langchain-azure-ai-foundry-mcp-servers-tools-memory-and-orchestration)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Why We Need Agents](#why-we-need-agents)
  - [Anatomy of an AI Agent](#anatomy-of-an-ai-agent)
  - [Frameworks for Building Agents](#frameworks-for-building-agents)
  - [Frameworks vs Providers](#frameworks-vs-providers)
  - [LangChain Fundamentals](#langchain-fundamentals)
    - [Demo](#demo)
  - [Set Up](#set-up)
  - [Tools and Function Calling](#tools-and-function-calling)
  - [MCP Server](#mcp-server)
    - [Self-Hosted Web Search](#self-hosted-web-search)
    - [Demo 4: MCP Web Search + Web Fetch](#demo-4-mcp-web-search--web-fetch)
  - [Dynamic Sessions](#dynamic-sessions)
    - [Demo 5: Python REPL in ACA Dynamic Sessions](#demo-5-python-repl-in-aca-dynamic-sessions)
    - [Demo 5.1: Upload File to Python Session](#demo-51-upload-file-to-python-session)
    - [Demo 5.2: Run Shell Commands in Session](#demo-52-run-shell-commands-in-session)
    - [Demo 5.4: Multi-Tool Agent in Dynamic Sessions](#demo-54-multi-tool-agent-in-dynamic-sessions)
    - [Demo 5.4.1: Download Files from the Session](#demo-541-download-files-from-the-session)
    - [Troubleshooting: Azure CLI Token Timeout](#troubleshooting-azure-cli-token-timeout)
  - [AI Agent Memory (Cosmos DB)](#ai-agent-memory-cosmos-db)
  - [Human in the loop](#human-in-the-loop)
  - [Before and After Model Hooks](#before-and-after-model-hooks)
  - [Sub agent orchestration](#sub-agent-orchestration)
  - [Logging and observability with LangSmith](#logging-and-observability-with-langsmith)

## Why We Need Agents

LLMs are powerful on their own, but they have limitations. Agents extend LLMs by allowing them to reason, decide, and take action.

Instead of only generating text, agents can:

- decide what to do next,
- call tools and functions,
- access memory and data,
- interact with external systems,
- involve humans when needed.

## Anatomy of an AI Agent

At the center of an AI agent is the **LLM**, which handles reasoning.

When we invoke an agent, it can interact with several surrounding components:

- **Tools / function calling**
- **MCP servers**
- **Sandbox environments**
- **Database / memory systems**
- **Human in the loop**

Together, these components turn the LLM from a text generator into an action-oriented system.

## Frameworks for Building Agents

Common frameworks for building AI agents include:

- LangChain / LangGraph
- Microsoft Agent Framework
- CrewAI
- OpenAI Agent SDK
- Google ADK
- LlamaIndex
- Claude Agent SDK

## Frameworks vs Providers

- **Framework**: how you build the agent workflow and orchestration logic.
- **Provider**: how the model actually runs or is hosted.

Examples of providers include:

- Azure AI Foundry
- OpenAI
- Anthropic
- Google AI Studio / Vertex AI
- AWS Bedrock
- DeepSeek
- Mistral AI

## LangChain Fundamentals

ReAct Agent stands for **Reason + Act**.

It runs in a loop:

1. The agent reasons about what to do next.
2. It takes an action (for example, by calling a tool).
3. It reads the observation/result.
4. If the task is not done, it loops back and continues.
5. Once answered, it stops.

So, it repeats until it solves the problem.

### Demo

1. Use Terraform to deploy an LLM in Azure AI Foundry.
   1. Deploy infrastructure from: `C:\GenAI\Agents\learning\Production-ready_AI_agents\infra`
   2. Save output values to `.env`.
   3. Go to Foundry Projects to see deployed models, endpoint, and API key.
2. Get endpoint and key.
3. Configure the client.
4. Build a ReAct agent.
5. Run `demo1.py`.

## Set Up

1. Set up a virtual environment:
   - `python -m venv agent_env`
   - `agent_env\Scripts\activate`
2. Install required base packages:
   - `pip install langgraph langchain langchain-openai python-dotenv`
3. For Azure scenarios, also install:
   - `pip install azure-ai-projects azure-identity msrest azure-keyvault-secrets azure-cognitiveservices-vision-computervision`
4. Create `requirements.txt` from your current environment:
   - `pip freeze > requirements.txt`
5. Or install packages from an existing `requirements.txt`:
   - `pip install -r requirements.txt`
6. Start building.

## Tools and Function Calling

- Tools give the agent the ability to do things (take actions).
- You can bind tools to a model and control when it can take action.
- A tool is defined with a simple `@tool` decorator.

1. Define tool
2. Bind to the model
3. Control invocation (force, allow, block)
4. Agent decides at runtime which tool fits the task
   1. Model chooses the tool, not you
   2. User asks a question -> model decides a tool is needed -> returns tool call with arguments -> application runs the tool -> result is returned to the model
5. Go to `Demo2.py`

## MCP Server

- Use MCP servers to expose external tools/resources in a standardized way so agents can discover and call them safely.
- MCP connects your model to external tools and data.
- MCP exposes tools over a standard protocol that MCP-compatible clients can consume.
- This is especially useful for remote-hosted tools over HTTP.
- For third-party hosted MCP servers, you usually only need the endpoint URL.
- Many frameworks (including LangChain) can sit on top of this model/tool calling pattern.
- In practice: the agent asks the MCP server what tools are available, then calls the right one.

Flow:

1. Connect agent to MCP server
2. Discover tool
3. Agent queries -> agent calls a tool to fetch docs
4. Grounded answer -> replies cite real docs

### Self-Hosted Web Search

- Taking MCP further means giving your agent reliable access to live web data.
  
1. Connect to a remote MCP server over Streamable HTTP.
2. Discover and invoke tools.
3. Add interceptors and error handling.
4. Fetch page content for grounding.

Two ways to run an MCP server:

Local and Remote.

- Local
  - Uses stdio
   - Agent _(stdio)_ -> Local server
   - Ideal for local development tools
- Remote
   - Runs over the network using Streamable HTTP
   - Agent _(HTTP)_ -> Hosted server
   - Calls a hosted server over the network
   - Scalable and shared
   - No local installs required
   - Can add interceptors or custom fetch tools on top of remote MCP
  - Interceptor: Logging, retries & error handling
  - Custom Fetch Tools - Read full web pages

### Demo 4: MCP Web Search + Web Fetch

`Demo4.py` demonstrates a production-oriented pattern where the agent combines:

- a **remote MCP search tool** (discovered from your hosted MCP server), and
- a **local fetch tool** (`fetch_webpage_content`) to retrieve and convert pages to Markdown.

It also includes resilience features:

- retry interceptor (with exponential backoff), and
- fallback interceptor (for timeout/connection failures).

Flow in `Demo4.py`:

1. Load Azure Foundry model config from `.env`.
2. Connect to remote MCP web-search server over HTTP.
3. Discover MCP tools and select the `search` tool.
4. Validate connectivity by invoking `search` directly.
5. Create an agent with:
   - remote `search` tool,
   - local `fetch_webpage_content` tool.
6. Ask a multi-step research question and stream final grounded output.

Required environment variables:

- `LLM_MODEL_DEPLOYMENT_NAME_CHATGPT`
- `FOUNDRY_API_KEY`
- `FOUNDRY_ENDPOINT`
- `ACA_MCP_SERVER_OPEN_WEB_SEARCH_FQDN`
- `APP_SERVICE_MCP_SERVER_OPEN_WEB_SEARCH_FQDN`

Run steps:

1. Run terraform file. This will create the App service for the MCP that will host the open web search
   - This creates a linux web app that will host a container using the container image coming from open web search
   - This is an open source project that provides an MCP server for searching the web using multiple search engines
2. Activate virtual environment:
   - `agent_env\Scripts\activate`
3. Set MCP server FQDN variables (PowerShell example):
   - `$env:ACA_MCP_SERVER_OPEN_WEB_SEARCH_FQDN="<your-aca-fqdn>"`
   - `$env:APP_SERVICE_MCP_SERVER_OPEN_WEB_SEARCH_FQDN="<your-appservice-fqdn>"`
4. Run demo:
   - `python Demo4.py`

Expected output:

- streamed model greeting,
- discovered MCP tools list,
- raw search verification output,
- final cited answer synthesized from fetched web content.

## Dynamic Sessions

Use dynamic sessions to maintain context per user/session, isolate state, and support long-running interactions.

- You can create a sandboxed code interpreter with Azure Container Apps Dynamic Sessions.
- This allows the agent to write and run real code safely.
- The environment can include Python REPL and Bash/Shell.
- Each session is a fresh isolated container, so execution is separated from your host environment.
- Inside the sandbox, the agent can run code and perform file I/O.
  
1. Spin up a Dynamic Session pool on ACA.
2. Use Python REPL to run code safely.
3. Use Bash/Shell to allow agents to execute commands.
4. Use File I/O to upload and download files.

Process:

1. Run Terraform. This creates Container App session pools for Python and Shell.
   - This uses Azure Container Apps to create sandboxes for both Python and Shell.
   - Configuration defines pool setup and dynamic pool management.
   - You will use the pool management endpoint to connect and send commands.
2. Activate virtual environment:
   - `agent_env\Scripts\activate`
3. Set Dynamic Session endpoints in your environment:
   - `SESSIONPOOL_MANAGEMENT_ENDPOINT_PYTHON`
   - `SESSIONPOOL_MANAGEMENT_ENDPOINT_SHELL`
   - (Optional) MCP endpoint variants if your flow uses them.
4. Run demo:
   - `python Demo5.py`

### Demo 5: Python REPL in ACA Dynamic Sessions

Goal:

- Ask the agent a question that requires actual code execution (for example: time-zone calculation).

What the demo does:

1. Builds an agent with `SessionsPythonREPLTool`.
2. Requests an access token for `https://dynamicsessions.io/.default`.
3. Sends Python code into the sandboxed session for execution.
4. Returns tool output back to the model for final response synthesis.

Example question:

- `What is the current time in Tunisia and France? Use the python REPL tool to get the answer.`

### Demo 5.1: Upload File to Python Session

Goal:

- Upload a JSON file into the sandbox session and reference it from executed Python code.

What this demonstrates:

1. Session file upload with `upload_file`.
2. Reading the uploaded file from the remote session path.
3. Computing a value from uploaded data (`sum`).

Flow in `Demo5.1.py`:

1. Initialize `SessionsPythonREPLTool` using `SESSIONPOOL_MANAGEMENT_ENDPOINT_PYTHON`.
2. Create an in-memory JSON payload.
3. Upload file to the session.
4. Execute Python code in-session to read JSON and compute a result.
5. Print upload metadata and execution output.

Run:

1. Activate virtual environment:
   - `agent_env\Scripts\activate`
2. Ensure env var is set:
   - `SESSIONPOOL_MANAGEMENT_ENDPOINT_PYTHON`
3. Execute:
   - `python Demo5.1.py`

Expected output:

- Remote uploaded file path.
- Execution result showing the computed sum from `important_data`.

### Demo 5.2: Run Shell Commands in Session

Goal:

- Show that `SessionsBashTool` executes commands inside the sandboxed container session, not on your host machine.

What this demonstrates:

1. Running shell commands in isolated dynamic sessions.
2. Inspecting session environment variables.
3. Reading code interpreter configuration.
4. Checking outbound IP from inside the session boundary.

Flow in `Demo5.2.py`:

1. Initialize `SessionsBashTool` using `SESSIONPOOL_MANAGEMENT_ENDPOINT_SHELL`.
2. Run connectivity check (`echo Hello from the session!`).
3. Run `printenv` to inspect session environment variables.
4. Run `cat /app/codeInterpreterConf.yaml` to inspect interpreter config.
5. Run `curl -s ifconfig.me/ip` to inspect outbound session IP.

Run:

1. Activate virtual environment:
   - `agent_env\Scripts\activate`
2. Ensure env var is set:
   - `SESSIONPOOL_MANAGEMENT_ENDPOINT_SHELL`
3. Execute:
   - `python Demo5.2.py`

Expected output:

- Structured JSON response for each command.
- Session environment and config details.
- Outbound IP address resolved from inside the sandbox.

### Demo 5.4: Multi-Tool Agent in Dynamic Sessions

Goal:

- Use both Python and Bash tools in one agent to complete end-to-end tasks in the sandbox.

What this demonstrates:

1. Building a single agent with both `SessionsPythonREPLTool` and `SessionsBashTool`.
2. Letting the model choose the right tool for each sub-task.
3. Running richer workflows (data fetch, package install, plotting, and file output) in isolated sessions.

Flow in `Demo5.4.py`:

1. Initialize both Dynamic Session tools:
   - `SessionsPythonREPLTool` using `SESSIONPOOL_MANAGEMENT_ENDPOINT_PYTHON`
   - `SessionsBashTool` using `SESSIONPOOL_MANAGEMENT_ENDPOINT_SHELL`
2. Create one agent with both tools.
3. Run a practical task prompt (for example: fetch 4 years of MSFT history and save `msft_4y.png`).
4. Stream tool decisions and model outputs.

Run:

1. Activate virtual environment:
   - `agent_env\Scripts\activate`
2. Ensure env vars are set:
   - `SESSIONPOOL_MANAGEMENT_ENDPOINT_PYTHON`
   - `SESSIONPOOL_MANAGEMENT_ENDPOINT_SHELL`
3. Execute:
   - `python Demo5.4.py`

Expected output:

- Visible tool-call traces (Python/Bash depending on task).
- Progress updates for package installs and code execution.
- Final artifact confirmation (for example, generated chart file path/name).

### Demo 5.4.1: Download Files from the Session

Goal:

- Move files between local machine and sandbox session, then retrieve generated artifacts.

What this demonstrates:

1. Uploading a local file into the session.
2. Listing files in the remote session.
3. Downloading a generated file from session to local output folder.
4. Optional local image preview.

Example workflow:

```python
# upload a file to the session
toolBashSession.upload_file(local_file_path="./rg.tf", remote_file_path="/mnt/user/rg.tf")

# list files in the session
files = toolBashSession.list_files()
print(files)

# download a file from the session
toolBashSession.download_file(
   remote_file_path="msft_5y.png",
   local_file_path="./output/msft_5y.png",
)

# optional: view the image locally
from PIL import Image
image = Image.open("./output/msft_5y.png")
image.show()
```

Run notes:

1. Ensure `./output` exists (or create it before download).
2. Ensure the remote file actually exists before download (for example after running chart-generation prompt).
3. If image preview fails, install Pillow locally:
   - `pip install pillow`

### Troubleshooting: Azure CLI Token Timeout

Observed issue:

- `CredentialUnavailableError: Failed to invoke the Azure CLI`
- Underlying cause: `az account get-access-token ... timed out`

Why it happens:

- The Python REPL tool depends on Azure CLI credential flow.
- If Azure CLI is not logged in, slow to start, or pointing at the wrong account/tenant, token acquisition can fail.

Fix steps:

1. Verify Azure CLI is installed and available:
   - `az --version`
2. Sign in:
   - `az login`
3. Verify current context:
   - `az account show`
4. If needed, select the correct subscription:
   - `az account set --subscription <subscription-id>`
5. Re-run:
   - `python Demo5.py`

Implementation note:

- In `Demo5.py`, token acquisition timeout was increased and error messaging was improved so failures provide clear recovery guidance.


## AI Agent Memory (Cosmos DB)

Use Cosmos DB-backed memory for persistence across sessions, user personalization, and long-term context retrieval.

## Human in the loop

Add human approval/review steps for high-risk or sensitive actions.

## Before and After Model Hooks

Use before/after model hooks to validate inputs, inject guardrails, and post-process outputs.

## Sub agent orchestration

Use sub-agent orchestration to split complex tasks into specialized responsibilities and aggregate results.

## Logging and observability with LangSmith

Use LangSmith for traces, evaluations, debugging, and performance monitoring of agent workflows.