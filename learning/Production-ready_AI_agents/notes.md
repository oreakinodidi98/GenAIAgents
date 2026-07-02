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
    - [What This Enables](#what-this-enables)
    - [LangGraph Memory Model](#langgraph-memory-model)
    - [InMemory vs Cosmos DB](#inmemory-vs-cosmos-db)
    - [Architecture](#architecture)
    - [Managing Long Conversations](#managing-long-conversations)
    - [Demo Mapping](#demo-mapping)
    - [End-to-End Memory Flow (Cosmos)](#end-to-end-memory-flow-cosmos)
    - [Troubleshooting Cosmos](#troubleshooting-cosmos)
    - [Create Manually (If Needed)](#create-manually-if-needed)
  - [Human in the loop](#human-in-the-loop)
    - [Why use HITL](#why-use-hitl)
    - [What happens at runtime](#what-happens-at-runtime)
    - [Human decisions](#human-decisions)
    - [Typical policy setup](#typical-policy-setup)
    - [Flow examples used in this repo](#flow-examples-used-in-this-repo)
    - [Notes and best practices](#notes-and-best-practices)
  - [Before and After Model Hooks](#before-and-after-model-hooks)
  - [Agent orchestration](#agent-orchestration)
    - [Why use sub-agents](#why-use-sub-agents)
    - [Core architecture](#core-architecture)
    - [When to use sub-agents](#when-to-use-sub-agents)
    - [When not to use sub-agents](#when-not-to-use-sub-agents)
    - [Benefits](#benefits)
    - [Orchestration types](#orchestration-types)
    - [Practical best practices](#practical-best-practices)
  - [Logging and observability with LangSmith](#logging-and-observability-with-langsmith)
    - [Why LangSmith](#why-langsmith)
    - [What to track](#what-to-track)
    - [Recommended practice](#recommended-practice)

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

Use Dynamic Sessions to run code in isolated, short-lived sandboxes while keeping your local machine safe.

Why this matters:

- You get real execution power (Python and Bash) without running untrusted code on your host.
- You can do file upload/download in the sandbox and move results back locally.
- You can combine shell + Python tools in a single agent workflow.

Core capabilities:

1. Python REPL execution.
2. Bash command execution.
3. Remote file upload/download.
4. Per-session isolation (clean boundary from host environment).

Setup and run sequence:

1. Provision Dynamic Session pools with Terraform (Python and Shell pools).
2. Activate virtual environment:
   - `agent_env\Scripts\activate`
3. Ensure environment variables are configured:
   - `SESSIONPOOL_MANAGEMENT_ENDPOINT_PYTHON`
   - `SESSIONPOOL_MANAGEMENT_ENDPOINT_SHELL`
4. Log in to Azure CLI:
   - `az login`
   - `az account show`
5. Run demos as needed:
   - `python Demo5.py`
   - `python Demo5.1.py`
   - `python Demo5.2.py`
   - `python Demo5.4.py`

### Demo 5: Python REPL in ACA Dynamic Sessions

Goal:

- Ask the agent a question that requires actual code execution (for example: time-zone calculation).

What the demo does:

1. Builds an agent with `SessionsPythonREPLTool`.
2. Requests an access token for `https://dynamicsessions.io/.default`.
3. Sends Python code into the sandboxed session for execution.
4. Returns tool output back to the model for final response synthesis.

Observed output pattern:

- Human prompt displayed.
- Tool call for `Python_REPL`.
- Tool output returned and summarized by the model.

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

Observed output pattern:

- Uploaded remote file path is printed.
- In-session computation result is printed (for the JSON sum).

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

Observed output pattern:

- Each command prints a structured JSON payload with:
   - `stdout`
   - `stderr`
   - `exitCode`
- This makes it easy to validate command success/failure programmatically.

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

Observed output pattern:

1. Agent calls Bash to check/import dependencies.
2. Agent installs missing packages (`yfinance`, `pandas`, `matplotlib`).
3. Agent generates chart and reports saved artifact (for example `msft_4y.png`).
4. Agent confirms date range and completion summary.

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

Important path guidance from demo runs:

- Prefer filename-style remote download paths (for example `msft_4y.png`) when using `download_file`.
- Absolute paths such as `/mnt/data/msft_4y.png` may fail depending on API expectations and URL path handling.
- In current demo flow, file transfer runs after chart generation to avoid early 404s.

Observed output pattern:

1. Upload response with remote metadata.
2. Session file listing showing generated artifacts.
3. Download response (or actionable error if artifact not present yet).
4. Optional local image preview if Pillow is installed.

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
- First token acquisition in a fresh shell can be slower on Windows.

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

Also check:

1. Ensure credential timeout is not too low in code.
2. Confirm endpoint environment variables are present and not empty.
3. Verify session pool endpoints belong to the same subscription/tenant context as your CLI login.

Implementation note:

- In `Demo5.py`, token acquisition timeout was increased and error messaging was improved so failures provide clear recovery guidance.

## AI Agent Memory (Cosmos DB)

Use memory to preserve context across turns and sessions.

### What This Enables

- Give agent short-term memory.
- Use a Cosmos DB checkpointer to persist the agent state.
- Manage multi-turn conversations (agent recalls earlier turns) with threads (separate memory per conversation thread).
- Summarize long thread conversations so they do not blow up and exceed the context window.
- Make memory useful and safe.
- Reduce tokens per request (less cost and lower latency) while keeping conversations coherent and affordable.

### LangGraph Memory Model

- Short-term memory in LangGraph is implemented via checkpointers, which save a snapshot of graph state at every step.
- You can assign a thread_id to a conversation. The checkpointer persists messages across invocations, so the agent remembers what was said earlier.

### InMemory vs Cosmos DB

- InMemorySaver works for prototyping, but it loses all state when the process restarts.
- For production workloads, use a durable backend.
- Azure Cosmos DB provides global distribution, serverless pricing, automatic indexing, and Microsoft Entra ID support for secure keyless authentication.

### Architecture

User -> LangGraph Agent -> Self-hosted LLM (vLLM on ACA)
                                 |
                                 v
                     CosmosDB Checkpointer
                     (persists conversation state per thread)

### Managing Long Conversations

- Long conversations can exceed the LLM context window.
- Solutions include:
   - Trim messages: remove first or last N messages before calling the LLM.
   - Delete messages: remove messages from LangGraph state if they are not useful.
   - Summarize messages: summarize earlier history and replace it with a summary.
   - Custom strategies: for example message filtering to send only important messages to the LLM.
- This allows the agent to track conversation state without exceeding the context window.
- Trimming/removing can lose important details from message culling. Some apps benefit from summarizing message history with a chat model.

### Demo Mapping

- Demo6.1.py shows summarization with InMemorySaver.
   - Uses InMemorySaver for summarization.
   - Can use different models.
- Demo6.py shows durable memory with Cosmos DB.

### End-to-End Memory Flow (Cosmos)

- Need the Cosmos DB instance deployed initially.
- Store required environment variables.
- Ensure model connectivity to Microsoft Foundry.
- Use the model to create a LangChain agent with memory.
- Create a Cosmos DB checkpointer.
- Start a multi-turn conversation.
- Use config with a thread ID to give each conversation a unique thread in Cosmos DB.
- In Cosmos DB Data Explorer, you can see persisted messages.

### Troubleshooting Cosmos

```powershell
az account set --subscription <value>

$rg = <"rg">
$account = "<name>"
$principal = <"ID">

$roleDefId = az cosmosdb sql role definition list `
   --resource-group $rg `
   --account-name $account `
   --query "[?roleName=='Cosmos DB Built-in Data Contributor'].id | [0]" `
   --output tsv

az cosmosdb sql role assignment create `
   --resource-group $rg `
   --account-name $account `
   --scope "/" `
   --principal-id $principal `
   --role-definition-id $roleDefId

az cosmosdb sql role assignment list `
   --resource-group $rg `
   --account-name $account `
   --query "[?principalId=='$principal']"
```

### Create Manually (If Needed)

```powershell
$acct = "cosmosdbagentmemorea629a1"

# Create DB expected by demo6.py
az cosmosdb sql database create `
   --resource-group $rg `
   --account-name $acct `
   --name "langgraph-memory"

# Create container expected by demo6.py
az cosmosdb sql container create `
   --resource-group $rg `
   --account-name $acct `
   --database-name "langgraph-memory" `
   --name "checkpoints" `
   --partition-key-path "/partition_key"
```

## Human in the loop

Add human approval/review steps for high-risk or sensitive actions.

### Why use HITL

- Pause agents to keep humans in control before risky actions.
- High-stakes tool calls get a human checkpoint before execution.
- For sensitive operations, a reviewer can inspect, edit, approve, or reject a proposed action.

### What happens at runtime

1. The model proposes a tool call.
2. If the tool matches your `interrupt_on` policy, `HumanInTheLoopMiddleware` emits an interrupt and pauses execution.
3. A human reviews pending actions.
4. The workflow resumes with one decision per pending action.

### Human decisions

- Approve: run the proposed tool call as-is.
- Edit: adjust arguments, then run the edited action.
- Reject: block execution and steer the agent to a safer path.
- Respond: send a human instruction back to the agent without running the tool.

### Typical policy setup

- `write_file`: interrupt and allow full decisions (`approve`, `edit`, `reject`, `respond`).
- `execute_sql`: interrupt but restrict to `approve` or `reject` (no SQL editing).
- `read_data`: allow directly with no interrupt.

### Flow examples used in this repo

- SQL flow: propose `execute_sql` -> interrupt appears -> human approves -> tool executes.
- File-write flow: propose `write_file` -> interrupt appears -> human edits path/content -> edited tool executes.

### Notes and best practices

- Use a checkpointer (for example `InMemorySaver`) because HITL pauses/resumes require persisted graph state.
- Keep `thread_id` stable for a given review session; use a different `thread_id` for independent sessions.
- If no interrupt appears, the model may have responded in text instead of issuing a tool call. Prompt more explicitly (for example: "Call the execute_sql tool now...").
- Log interrupts and final decisions for auditability.

## Before and After Model Hooks

Use before/after model hooks to validate inputs, inject guardrails, and post-process outputs.

- More fine grained control
- Run custom logic before and after each model call
- Allows you to inspect, modify or guard agent behaviour automatically
- This allows us to access and manipulate the agent's short-term memory (state) at different stages of the agent's execution
- run code before and after model calls in LangChain agents using @before_model and @after_model middleware
- Before hook: inspects/rewrite the prompt
- model call: The LLM generates a responce
- After hook: Inspect or Modify the output
- Guard: Enforce policies with midldleware
- The middleware hooks wrap each model call

## Agent orchestration

Use sub-agent orchestration to split complex tasks into specialized responsibilities and aggregate results.

### Why use sub-agents

- Sub-agents solve the context-bloat problem.
- When agents use tools with large outputs (web search, file reads, database queries), the context window fills quickly with intermediate results.
- Sub-agents isolate detailed work. The main agent receives only final summaries, not dozens of intermediate tool calls.

### Core architecture

- A main agent coordinates subagents as tools.
- All routing passes through the main agent.
- In this architecture, a central main agent (often called a supervisor) calls subagents as tools.
- The main agent decides which subagent to invoke, what input to provide, and how to combine results.
- Subagents are typically stateless and do not remember past interactions.
- Conversation memory is maintained by the main agent.
- This provides context isolation: each subagent invocation starts with a clean context window, reducing context bloat in the main conversation.

### When to use sub-agents

- Multi-step tasks that would clutter the main agent context.
- Specialized domains that need custom instructions or tools.
- Tasks requiring different model capabilities.
- Workflows where you want the main agent focused on high-level coordination.
- Scenarios with multiple distinct domains (for example calendar, email, CRM, or database).
- Cases where subagents do not need to converse directly with users.
- Systems that require centralized workflow control.

### When not to use sub-agents

- Simple single-step tasks.
- Cases where you must maintain all intermediate context in one place.
- Situations where orchestration overhead outweighs the benefits.

### Benefits

- Faster execution.
- Less error-prone execution.
- Lower cost.

### Orchestration types

1. Supervisor: one lead agent organizes and delegates tasks.
2. Sequential: each agent hands output to the next agent.
3. Parallel: multiple agents run at the same time and results are aggregated.
4. Handoff: one agent passes control to another agent.

### Practical best practices

- Keep clear contracts for each subagent tool (inputs, outputs, and failure behavior).
- Return compact, structured outputs from subagents to reduce token use.
- Add fallback handling when one subagent fails so the main agent can continue with partial results.
- Log routing decisions (which subagent was called and why) for debugging and auditability.

## Logging and observability with LangSmith

Use LangSmith for traces, evaluations, debugging, and performance monitoring of agent workflows.

### Why LangSmith

- Gives full visibility into every agent run.
- Enables tracing across model calls, tool calls, and middleware steps.
- Lets you inspect calls and intermediate states.
- Helps debug failures and improve quality over time.
- Makes LLM systems observable and easier to reason about.

### What to track

- End-to-end run traces.
- Tool call inputs and outputs.
- Latency and token usage per step.
- Errors, retries, and fallback paths.
- Prompt and response changes during iteration.

### Recommended practice

- Trace every run in development.
- Keep tracing enabled in staging/production with appropriate sampling.
- Use consistent run metadata (environment, version, scenario, thread_id) for easier filtering.
- Review traces regularly to identify bottlenecks, prompt issues, and tool reliability problems.