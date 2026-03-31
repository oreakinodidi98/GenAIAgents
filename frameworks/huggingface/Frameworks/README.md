# Different agentic frameworks

## Background

- Agentic framework is not always needed when building an application around LLMs.
- They provide flexibility in the workflow to efficiently solve a specific task, but they’re not always necessary.
- Sometimes, predefined workflows are sufficient
- If the approach to build an agent is simple, like a chain of prompts, using plain code may be enough.
- The advantage is that the developer will have full control and understanding of their system without abstractions.
- However, when the workflow becomes more complex abstractions start to become helpful.

## Smolagents (Agents framework developed by Hugging Face.)

- smolagents is a framework for building AI agents.
- AI agents are programs that use LLMs to generate ‘thoughts’ based on ‘observations’ to perform ‘actions’.
- Code agents are the default agent type in smolagents. 
  - They generate Python tool calls to perform actions, achieving action representations that are efficient, expressive, and accurate.
  - This approach reduces the number of required actions, simplifies complex operations, and enables reuse of existing code functions.
- Research shows that tool-calling LLMs work more effectively with code directly

### Why

- open-source agent frameworks available for application development
- **CodeAgents** are the primary type of agent in smolagents.
  - Instead of generating JSON or text, these agents produce Python code to perform actions
- **ToolCallingAgents** are another type of agents supported by smolagents.
  - These agents rely on JSON/text blobs that the system must parse and interpret to execute actions.
- **Retrieval agents** allow models access to knowledge bases, making it possible to search, synthesize, and retrieve information from multiple sources.
  - Useful for integrating web search with custom knowledge bases while maintaining conversation context through memory systems
- **Vision agents** extend traditional agent capabilities by incorporating Vision-Language Models (VLMs), enabling them to process and interpret visual information.
- **Simplicity**: Minimal code complexity and abstractions, to make the framework easy to understand, adopt and extend
- **Flexible LLM Support**: Works with any LLM through integration with Hugging Face tools and external APIs
- **Code-First Approach**: First-class support for Code Agents that write their actions directly in code, removing the need for parsing and simplifying tool calling
- **HF Hub Integration**: Seamless integration with the Hugging Face Hub, allowing the use of Gradio Spaces as tools

### When to use

- Lightweight and minimal solution.
- Experiment quickly without complex configurations.
- Application logic is straightforward.

### Example in this folder

- Run `smolagents_demo.py` for a minimal self-contained `CodeAgent` example.
- The demo does not require `ddgs` because it uses a local tool instead of `DuckDuckGoSearchTool`.

## Llamaindex (End-to-end tooling to ship a context-augmented AI agent to production)

## LangGraph (Agents allowing stateful orchestration of agents)

## Prerequisites

- Python 3.10 or later
- A Hugging Face account
- A Hugging Face access token stored as `HF_TOKEN`

## Setup

### 1. Create and activate the virtual environment

```powershell
python -m venv agent_venv
& .\agent_venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install python-dotenv huggingface_hub smolagents pytz
pip install ddgs
pip install opentelemetry-sdk opentelemetry-exporter-otlp openinference-instrumentation-smolagents langfuse
```

Optional extras:

```powershell
pip install "smolagents[littellm]"
```

### 3. Configure environment variables

Create a `.env` file in this directory:

```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HF_MODEL_ID=Qwen/Qwen2.5-Coder-32B-Instruct
```

### 4. Run the demo

```powershell
python smolagents_demo.py
```

### 5. Expected behavior

- The script logs in with `HF_TOKEN` if it is present.
- The agent calls a small local tool and prints the final answer in the terminal.
- If you want to switch models, change `HF_MODEL_ID` in `.env`.

### 6. push and download agent

# Change to your username and repo name
agent.push_to_hub('oreakinodidi98/DemoAgent')
# Change to your username and repo name
demo_agent = agent.from_hub('oreakinodidi98/DemoAgent', trust_remote_code=True)

demo_agent.run("Give me the best playlist for a party at Wayne's mansion. The party idea is a 'villain masquerade' theme")  