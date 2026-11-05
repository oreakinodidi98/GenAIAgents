---
description: Hands-on notes on LangChain agents, tools, MCP, code execution, and conversation memory.
---

# LangChain Fundamentals

## Introduction

Before we start building, let's separate three things that are easy to mix up: the agent, the framework, and the model provider. They work together, but each has a different role.

- An **agent** is software that takes in information, decides what to do next, and takes action towards a goal. In an LLM-based agent, the model helps decide when to use a tool and how to respond.
- A **framework** helps us build and connect the parts of the agent. In these examples, we use LangChain.
- A **model provider** hosts the model and gives our application a way to use it. Microsoft Foundry is one example.

The way I think about it is: the provider gives us access to the model, LangChain helps us connect the pieces, and the agent uses those pieces to get a task done.

## Module 1: LangChain fundamentals

Let's start by connecting to a model and creating a basic agent. We won't add tools yet, so we can first make sure the model connection is working.

### 1. Set up the Python environment

A virtual environment keeps the packages for this project separate from your other Python projects. From the repository root, open PowerShell and run:

```powershell
Set-Location .\Frameworks\Langchain\Fundamentals
python -m venv agent_env
.\agent_env\Scripts\Activate.ps1
```

If PowerShell blocks activation, skip that step and use `.\agent_env\Scripts\python.exe` in place of `python` for the commands that follow.

Install the project's packages:

```powershell
python -m pip install -r requirements.txt
```

When you open a new terminal later, return to this folder and activate the environment again.

### 2. Set up the infrastructure and model deployment

To call a model, we need a Microsoft Foundry resource and a model deployment. If you already have access to both, you can use them and skip the Terraform steps.

If you need to create the resources, we can use the [Terraform configuration](../IAC/). Terraform is an Infrastructure as Code (IaC) tool: we describe the resources in configuration files, review the proposed changes, and then choose whether to create them.

> [!IMPORTANT]
> The Terraform configuration also includes resources for later modules. Review the names, region, model availability, quotas, and costs before deploying. You will need Terraform, the Azure CLI, and access to an Azure subscription.

1. Sign in to Azure and select the subscription you want to use:

   ```powershell
   az login
   az account set --subscription "<subscription-id>"
   ```

2. Review the [Terraform variables](../IAC/variables.tf) and set values for your environment. From the `Fundamentals` folder, initialise Terraform and preview the changes:

   ```powershell
   Set-Location ..\IAC
   terraform init
   terraform validate
   terraform plan
   ```

3. If the plan is what you want, run `terraform apply`. Terraform generates a new plan for the apply, so review it before confirming.

4. After a successful deployment, get the Foundry resource endpoint and model deployment name. For example, from the `IAC` folder, get the endpoint and the GPT deployment name, then return to the `Fundamentals` folder:

   ```powershell
   terraform output -raw foundry_endpoint
   terraform output -raw llm_model_deployment_name_chatgpt
   Set-Location ..\Fundamentals
   ```

If you are using an existing deployment, get these values from the Azure portal instead. For the later tool examples, choose a deployed model that supports tool calling.

#### Configure the application

The endpoint tells the application where to send requests, while the deployment name tells it which model deployment to use. The scripts in these modules load those values from a local `.env` file.

From the `Fundamentals` folder, create the file from the example if it does not already exist:

```powershell
if (-not (Test-Path .\.env)) {
    Copy-Item .\.env.example .\.env
}
```

In `.env`, fill in these two values, replacing the placeholders:

```text
FOUNDRY_ENDPOINT=<your-foundry-resource-endpoint>
LLM_MODEL_DEPLOYMENT_NAME=<your-model-deployment-name>
```

Use the resource endpoint without a trailing slash, not the project endpoint. The script adds `/openai/v1` to the resource endpoint, so don't include that path in the value yourself. The deployment name is the name of your deployed model, which may be different from the model's original name.

The examples use `DefaultAzureCredential` to authenticate with Microsoft Entra ID. If you are using Azure CLI credentials, run `az login` and make sure the identity selected by `DefaultAzureCredential` has permission to call the model deployment. Adding an API key to `.env` alone does not change the authentication used by these scripts.

> [!IMPORTANT]
> Keep API keys and other secrets out of source control and logs. The `.env` file is for your local configuration, not for sharing credentials.

### 3. Configure the client and build a ReAct agent

In [module1.py](./module1.py), we configure the model client using the endpoint, deployment name, and authentication. We then test a response from the model directly before creating an agent around it.

ReAct stands for **Reason + Act**. The idea is that an agent can decide what to do, request an action, look at the result, and use that result to decide what comes next.

Here is the flow when tools are available:

```text
User request
     |
     v
Agent decides what to do
     |
     +--> Answer directly
     |
     +--> Request a tool
              |
              v
        Application runs the tool
              |
              v
        Result returned to the agent
              |
              +--> Answer or request another tool
```

For example, if you ask about the weather, an agent with a weather tool can request it and use the result in its answer. The agent can also answer without a tool when one isn't needed. The diagram describes the decision-and-action loop; it doesn't mean the agent has to show its internal reasoning.

Run the first example from the `Fundamentals` folder:

```powershell
python .\module1.py
```

You should see a streamed response from the model, followed by a response from the agent. This first agent has no tools yet. If the connection fails, check the resource endpoint, deployment name, sign-in, and model access before moving on.

For more on the agent loop, see the [LangChain agent documentation](https://docs.langchain.com/oss/python/langchain/agents).

## Module 2: Tools and function calling

A model can generate a response, but it doesn't automatically have access to our APIs, files, or business systems. Tools give the agent specific actions it can request, such as multiplying numbers, searching documentation, or calling a weather service.

The model decides whether to request a tool based on the question and the tools we make available. We still decide which tools the agent can use and what those tools are allowed to do.

### How we set up a tool

1. Write a function that performs the action.
2. Give it a clear name, description, and typed arguments so the model can understand when and how to use it.
3. Register the tool with the agent. If you are handling tool calls directly, you can bind it to the model instead.
4. Set any permissions and restrictions needed before the function runs.

In LangChain, the `@tool` decorator can turn a Python function into a tool. For example:

```python
from langchain_core.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b
```

The function name and description tell the model what the tool does. The type hints describe the inputs it expects. Clear descriptions matter because the model uses this information when deciding whether to request the tool.

### What happens during a tool call

1. The user asks a question.
2. The model decides whether it needs a tool.
3. If it does, the model returns a tool call containing the tool name and arguments.
4. The application or agent framework runs the requested function.
5. The tool result goes back to the model.
6. The model uses the result to answer or requests another tool if more work is needed.

So this is a round trip: the model requests the action, but the application executes it. That distinction matters because we still need to enforce permissions, validate inputs, and handle errors in the application, not only in the prompt.

In [module2.py](./module2.py), we register a `multiply` tool and a `get_weather` tool, then ask the agent to use them. The weather tool generates random demo data; it does not connect to a real weather service. Run it from the `Fundamentals` folder:

```powershell
python .\module2.py
```

## Module 3: Model Context Protocol

Model Context Protocol (MCP) is an open standard for connecting AI applications to external tools and information. Instead of building a separate integration for every agent, we can expose capabilities through an MCP server and connect to them using an MCP client.

I think of MCP a bit like USB for agent integrations: it gives applications and servers a common way to connect. The server still determines which capabilities it provides and who can use them.

An MCP server can expose:

- Tools that perform actions, such as searching documentation
- Resources that provide data or context
- Prompts that provide reusable interaction templates

The pieces fit together like this:

```text
User request
     |
     v
LangChain agent
     |
     v
MCP client <----> MCP server
                       |
                       +-- Tools
                       +-- Resources
                       +-- Prompts
```

### How the agent uses an MCP server

In [module3.py](./module3.py), `MultiServerMCPClient` connects to the Microsoft Learn MCP server, gets its tools, and makes those tools available to the LangChain agent. This example loads tools; resources and prompts are not automatically passed to the agent.

After completing the model setup in Module 1, run the example from the `Fundamentals` folder:

```powershell
python .\module3.py
```

The script asks about Azure Container Apps, and the agent can use the discovered tools to look up information from Microsoft Learn. Here's how the tool flow works:

1. The application's MCP client connects to the server.
2. It discovers the tools that the server exposes.
3. Those tools are made available to the agent.
4. The agent requests a tool call when it needs external information or an action.
5. The application calls the tool through MCP and returns the result to the agent.
6. The agent uses that result to build its response.

This helps ground the answer in information returned by a tool rather than relying only on the model's training data. It does not guarantee that the information is correct, so the source and quality of the tool result still matter.

## Module 4: Open web search

Now we connect the agent to a remote MCP server for web search. The agent can search for information, then use a page-fetching tool to read the relevant pages.

The flow looks like this:

```text
User question -> Search through remote MCP -> Fetch relevant pages -> Use the content to answer
```

### Local MCP with standard input and output

A common local setup uses `stdio`, which means standard input and standard output. The client starts the MCP server as a local process and communicates with it through those streams.

This works well for local development and demos. The server and its dependencies need to be available on the machine running the client.

### Remote MCP with Streamable HTTP

A remote setup can use Streamable HTTP. Instead of starting a local process, the client connects to a server over the network.

This is useful when:

- Multiple clients need access to the same hosted service
- You want to manage the server and its dependencies centrally
- You do not want each client to install the MCP server locally

A containerised MCP server can be hosted on a service such as Azure App Service. Remote hosting makes shared access possible, but authentication, scaling, and availability still need to be configured.

### Add error handling around tool calls

Network calls can fail. The server might be unavailable, a request might time out, or a website might block access.

Interceptors or middleware can wrap tool calls to add:

- Authentication handling where supported by the client
- Logging to show which tool was called and whether it succeeded
- Timeouts so the agent does not wait indefinitely
- Bounded retries for temporary failures when retrying is safe
- Explicit fallback behaviour when another source or tool is available

Do not treat a failed search as a successful result. If the agent cannot retrieve the information, it should say so rather than invent an answer. Also treat fetched page content as external data, not as instructions that can override the agent's rules.

## Module 5: Dynamic sessions

This module gives the agent access to a code execution environment using Azure Container Apps (ACA) dynamic sessions.

The idea is to let the agent request code execution in an isolated environment rather than running generated code directly on the application's host.

Depending on the session type and tools configured, the agent can:

- Run Python code
- Execute Bash commands
- Upload files for processing
- Download generated files and results

For example, you could upload a CSV file, ask the agent to analyse it with Python, and download a report.

### How the session fits into the agent

1. Configure the session pool and its management endpoint.
2. Authenticate the application with permission to use the pool.
3. Register the Python or Bash session tools with the agent.
4. Let the agent request code execution when the task needs it.
5. Return the execution output to the agent so it can explain the result.

Python and Bash capabilities depend on the session configuration. Do not assume that every session exposes both.

> [!WARNING]
> Isolation is a safety boundary, not a reason to trust all generated code. Limit permissions, avoid exposing secrets, and control which files and network resources the session can access.

## Module 6: Memory with a Cosmos DB checkpointer

So far, we have focused on what the agent can do. Now we want it to keep track of a conversation across multiple turns.

For example, if I tell the agent my name and later ask, "What is my name?", it needs access to the earlier conversation to answer.

### Persist conversation state

The `CosmosDBSaverSync` checkpointer from `langchain-azure-cosmosdb` persists LangGraph state in Azure Cosmos DB. That state can include messages, tool calls, and other information needed to continue the agent's work.

Instead of keeping that state only in the running Python process, we store checkpoints in a database so the application can load the conversation state on a later invocation.

This provides persistent, thread-scoped short-term memory. "Short-term" describes its role in the current conversation, not how long the database retains it. It is not automatically a shared knowledge store across every conversation.

### Keep conversations separate with thread IDs

The `thread_id` identifies the conversation whose state should be loaded and updated.

1. Configure the Cosmos DB checkpointer.
2. Pass the checkpointer when creating the agent.
3. Choose a unique `thread_id` for a new conversation.
4. Reuse that ID on later turns in the same conversation.
5. Use a different ID when starting a separate conversation.

In the demo, messages sent with `demo-thread-1` share conversation state. A request using `demo-thread-2` starts a separate thread and should not have access to the first thread's history.

> [!IMPORTANT]
> A thread ID separates stored conversation state, but it is not an authorisation mechanism. The application must verify that the signed-in user is allowed to access the requested thread.

You can inspect the Cosmos DB container to confirm that checkpoints are being saved. Look for the stored state and thread identifiers. Do not assume that every message or tool call is stored as its own document; the document layout depends on the checkpointer implementation.

### Manage long conversations

Saving conversation history does not give the model an unlimited context window. The context window is the amount of information the model can process in one request.

As the conversation grows, sending the full history can increase token usage, cost, and latency. Eventually, the request may exceed the model's context limit.

There are a few ways to manage this:

- Trim messages to send only a selected part of the history to the model, without necessarily changing the persisted state.
- Delete messages to remove selected entries from the active conversation state. This does not necessarily erase older database checkpoints.
- Summarise earlier messages and keep the summary alongside recent messages.
- Apply custom filtering to retain information relevant to the current task.

When trimming or deleting messages, keep tool calls paired with their results so the remaining history is still valid.

### Summarise instead of dropping everything

Trimming history is straightforward, but it can remove something the agent still needs. For example, an early message might contain a user preference, a requirement, or a decision that matters later.

Summarisation gives us another option. A chat model condenses older messages into a shorter summary, while recent messages remain available in more detail.

In this demo, `SummarizationMiddleware` is configured with a token-based trigger and a setting to retain recent messages. These settings need to fit the model's context window and the conversation pattern.

The flow is:

1. Track the growing conversation history.
2. Trigger summarisation when the configured threshold is reached.
3. Condense older history into a summary.
4. Keep recent messages alongside that summary.
5. Continue the conversation using the smaller context.

A summary can still lose detail or introduce mistakes. Preserve critical facts carefully, and remember that generating the summary also uses tokens.

The way I think about it: short-term memory keeps the conversation coherent, and summarisation helps keep the context manageable and the token cost under control.

### Choose the right memory backend

`InMemorySaver` is useful for demos and prototyping because it keeps the setup small. However, it stores state in the running process, so that state is lost when the process restarts.

If the conversation needs to survive a restart, use a durable checkpointer such as the Cosmos DB checkpointer. Azure Cosmos DB supports features such as global distribution, automatic indexing, and Microsoft Entra ID authentication. These still need to be configured for your workload, and the checkpointer must support the authentication method you choose.

The distinction is simple: in-memory storage helps us test the flow, while durable storage lets us resume it later.

## Module 7: Human-in-the-loop middleware

Now we want the agent to pause before it runs a sensitive tool. For example, I might let it read data without asking, but I want to review a database change or file write before it happens.

This is where `HumanInTheLoopMiddleware` comes in. It checks proposed tool calls against the policy we configure and pauses the ones that need review.

The flow looks like this:

```text
Agent requests a tool -> Middleware pauses execution -> Human reviews the action -> Resume with a decision
```

### Decide which tools need approval

Configure the `interrupt_on` mapping when adding the middleware:

- Set a tool to `True` to pause its calls and allow the default review decisions.
- Set a tool to `False` when its calls do not need a review pause.
- Set `allowed_decisions` explicitly when you want to limit the reviewer's options.

In the demo, `write_file` is set to `True`, while `execute_sql` only allows approval or rejection. Tools such as `multiply` do not require approval.

Setting `write_file` to `True` does not mean the tool is automatically approved. It means the tool call must pause for a decision.

### Review the proposed action

The main decisions we use here are:

- Approve to run the proposed action with its existing arguments.
- Edit to change the proposed action's arguments before it runs.
- Reject to prevent that proposed action from running and return feedback to the agent.

For example, the agent might propose writing to one file, but the reviewer changes the destination and content before allowing the write.

### Pause and resume the agent

1. Add the human-in-the-loop middleware and configure the tools that require review.
2. Attach a checkpointer so the agent's execution state can be saved during the pause.
3. Invoke the agent with a `thread_id`.
4. Inspect the interrupt and show the proposed tool name and arguments to the reviewer.
5. Collect a decision and resume using `Command(resume=...)` with the same thread ID.

In the demo's `version="v2"` invocation, the result is a `GraphOutput`. Its `.interrupts` attribute contains the pending review requests, and `.value` contains the graph's output state.

> [!IMPORTANT]
> The demo supplies approval and edit decisions directly in code to show how resuming works. A real human review flow must wait for an authorised person's decision rather than automatically sending approval.

This gives us a review gate for the tools we configure. It does not replace permissions, argument validation, or checks inside the tools themselves.

## Module 8: Before and after model calls

Human-in-the-loop middleware pauses for a person's decision. Before and after model hooks let us apply custom logic automatically around each model call.

These hooks give us more control over what the model receives and what happens after it responds.

```text
Before-model hook -> Model call -> After-model hook -> Continue the agent loop
```

An agent can call the model several times while handling one user request, so these hooks can also run several times during that request.

### Before the model call

Use `@before_model` to inspect the agent's state and return any required updates before the next model call.

For example, you might trim older messages so the next request contains a smaller conversation history. In the demo, the hook keeps the first message and a small set of recent messages.

The aim is to control the context sent to the model. Be careful not to remove information the agent still needs or separate a tool call from its result. If the hook updates the state's message list, it can also change the history that gets checkpointed.

### After the model call

Use `@after_model` to inspect the updated state after the model responds. You can apply validation or return state updates before the agent continues.

For example, the demo checks the latest message for the words `password` and `secret` and removes the message if it finds either.

That shows how the hook works, but it is not a complete sensitive-data filter. A keyword check can block harmless text and miss actual secrets.

### Add hooks to the agent

1. Define the function and decorate it with `@before_model` or `@after_model`.
2. Inspect the state and decide whether an update is needed.
3. Return a state update when something needs to change, or `None` when no update is needed.
4. Register the hook in the agent's `middleware` list.
5. Test both the normal path and the path where the hook changes the state.

The key idea: prompts tell the model how we want it to behave, while middleware lets the application apply checks at specific points in execution. A hook only enforces the logic we actually implement; it does not automatically add retries, redaction, or protection for streamed output.

## Module 9: Subagents

As tasks become more complex, we do not always want one agent handling every step with every available tool.

Instead, a main agent can delegate a focused piece of work to a subagent. The subagent gets its own instructions and the tools needed for that task, then returns a result to the main agent.

The main agent stays responsible for coordinating the work and putting the final answer together.

### How the research example works

In this example, the main agent has access to MCP search tools. The research subagent has a page-fetching tool and is asked to summarise one page at a time.

The flow is:

1. The user asks a research question.
2. The main agent searches for relevant sources through MCP.
3. It passes a selected URL and the research question to a subagent through a tool wrapper.
4. The subagent fetches the page and returns a focused summary.
5. The main agent brings the summaries together, highlights any gaps, and includes the sources in its answer.

```text
User question -> Main agent searches -> Subagent reads and summarises a page -> Main agent combines the findings
```

Each agent should get the tools it needs. Not every subagent needs its own MCP connection; it can also use ordinary application tools, as the page-reading subagent does here.

### Why use a subagent

- Keep each agent focused on a smaller task
- Keep raw page content out of the main agent's context when a summary is enough
- Separate specialist instructions and tool access
- Make a complex workflow easier to inspect and debug

For example, the main agent does not need every line from every webpage. It needs useful findings, their sources, and any limitations.

### Know the trade-offs

Subagents do not automatically mean fewer tool calls, lower cost, or faster responses. Delegation adds model calls and coordination work, and summaries can lose important details.

Independent tasks can run in parallel if the implementation supports it, but adding a subagent alone does not guarantee parallel execution.

Use subagents when the separation helps with the task. If one agent can handle the work clearly with a few tools, keep it simple.

## Module 10: Logging and observability

Once an agent uses models, tools, middleware, and subagents, the final answer does not tell us everything that happened along the way.

We need to see which calls ran, what failed, where time was spent, and whether the agent followed the intended workflow. This is what logging and observability help us understand.

### Logs and traces

Logs record individual events, such as a tool starting, failing, or completing. Traces connect related operations so we can follow a request through the agent's workflow.

LangSmith can capture supported LangChain model and tool calls, along with nested subagent runs. Custom functions can also be instrumented with `@traceable` where needed.

The flow is:

```text
Enable tracing -> Run the agent -> Inspect model and tool calls -> Find issues -> Improve and rerun
```

### What to inspect

1. Configure tracing and select the project where runs should appear.
2. Run a representative request through the agent.
3. Open its trace and follow the model calls and tool calls.
4. Check what the main agent delegated and what the subagent returned.
5. Review errors, retries, latency, and token usage where available.
6. Make a focused change and rerun the request to check whether it helped.

For the research example, this lets us check whether the main agent found useful sources, whether the subagent fetched the right pages, and whether the final response reflects the returned summaries.

> [!IMPORTANT]
> Traces can contain prompts, user messages, tool arguments, and tool results. Review what is captured, remove secrets and sensitive data, and confirm that sending it to the tracing service is allowed before enabling tracing for real workloads.

The goal is to turn a black box into a workflow we can inspect. Instead of guessing why the agent gave a particular answer, we can look at the calls and results that led to it.
