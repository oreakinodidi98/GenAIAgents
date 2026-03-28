# AI Agent Fundamentals

> A comprehensive guide to understanding AI agents, large language models, tools, and agent workflows.

## Table of Contents

- [What Is an Agent?](#what-is-an-agent)
- [Large Language Models (LLMs)](#large-language-models-llms)
- [Messages and Chat Templates](#messages-and-chat-templates)
- [Tools](#tools)
- [Model Context Protocol (MCP)](#model-context-protocol-mcp)
- [AI Agent Workflow](#ai-agent-workflow)
  - [Thoughts](#thoughts)
  - [Actions](#actions)
  - [Observations](#observations)

---

## What Is an Agent?

An **Agent** is software that perceives its environment and reacts to a command (a user-defined objective). It is an AI model capable of **reasoning**, **planning**, and **interacting** with its environment.

- **ReAct** = Reason + Act
- **Act** = Use tools from a known tool set

### Anatomy of an Agent

An agent has two core parts:

| Part | Role |
|------|------|
| **Brain** (AI Model) | Handles reasoning and planning. Decides which actions to take based on the situation. |
| **Body** (Tools & Capabilities) | Everything the agent is equipped to do — the tools and interfaces it can interact with. |

### Tools vs. Actions

- **Tools**: Functions an agent can call to complete actions.
- **Actions**: Higher-level steps that may involve the use of *multiple* tools to complete.

---

## Large Language Models (LLMs)

An LLM is a type of AI model that excels at understanding and generating human language. Most modern LLMs are built on the **Transformer** architecture — a deep learning architecture based on the "Attention" algorithm.

### Transformer Types

| Type | Description |
|------|-------------|
| **Encoder** | Takes text as input and outputs a dense representation (embedding) of that text. |
| **Decoder** | Generates new tokens to complete a sequence, one token at a time. |
| **Seq2Seq** (Encoder-Decoder) | Combines an encoder and decoder. The encoder processes the input into a context representation; the decoder generates the output sequence. |

LLMs are typically **decoder-based** models with billions of parameters.

### Key Concepts

- **Next-token prediction**: The core objective — predict the next token given a sequence of previous tokens.
- **Token**: The unit of information an LLM works with. Think of it as a sub-word unit (not always a whole word) chosen for efficiency.
- **Autoregressive**: The output from one pass becomes the input for the next, until the model emits an **EOS** (End of Sequence) token.
- **Context length**: The maximum number of tokens the LLM can process at once — its maximum attention span.
- **Prompt**: The input sequence you provide to an LLM. The model predicts the next token by looking at every input token and choosing which ones are "important."

### How Token Prediction Works

1. The input text is tokenized. The model computes a representation capturing the meaning and position of each token.
2. This representation is passed through the model, which outputs scores ranking the likelihood of each vocabulary token being the next one.
3. A **decoding strategy** selects the next token based on these scores (e.g., greedy decoding picks the highest-scoring token).
4. This process repeats until the sequence is complete.

### Training

LLMs are trained on large datasets of text, learning to predict the next word via **self-supervised** or **masked language modeling** objectives.

---

## Messages and Chat Templates

### System Messages

Also called **System Prompts**, these define how the model should behave:

- Serve as persistent instructions guiding every subsequent interaction.
- Provide information about available tools.
- Define how the model should format actions and segment its thought process.

### User and Assistant Messages

A conversation consists of alternating messages between a **User** (human) and an **Assistant** (LLM).

### Chat Templates

Chat templates are essential for structuring conversations between language models and users:

| Model Type | Description |
|------------|-------------|
| **Base Model** | Trained on raw text data to predict the next token. |
| **Instruct Model** | Fine-tuned specifically to follow instructions and engage in conversations. |

To make a Base Model behave like an Instruct Model, prompts must be formatted consistently using **chat templates** that the model can understand.

---

## Tools

A **Tool** is a function given to the LLM that fulfills a clear objective. A good tool complements the LLM's capabilities.

### Tool Components

| Component | Description |
|-----------|-------------|
| **Description** | Textual description of what the function does. |
| **Callable** | The function that performs the action. |
| **Arguments** | Typed input parameters. |
| **Outputs** *(optional)* | Typed return values. |

### Example

```python
@tool
def calculator(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

print(calculator.to_string())
```

---

## Model Context Protocol (MCP)

**Model Context Protocol (MCP)** is an open protocol that standardizes how applications provide tools to LLMs.

### Benefits

- A growing list of **pre-built integrations** that LLMs can plug into directly.
- **Flexibility** to switch between LLM providers and vendors.
- **Best practices** for securing data within your infrastructure.

### Architecture

- **Skills** are Markdown instruction files that teach the AI *what to do* and *when*.
- **MCP servers** handle execution.
- The knowledge layer and tool layer evolve and ship **independently**.

> **Why Tools Are Essential**: They enable agents to overcome the limitations of static model training, handle real-time tasks, and perform specialized actions.

---

## AI Agent Workflow

Agents operate in a continuous loop of three phases:

```
Thought -> Action -> Observation -> (repeat until objective is fulfilled)
```

| Phase | Description |
|-------|-------------|
| **Thought** | The LLM decides what the next step should be. |
| **Action** | The agent calls tools with the associated arguments. |
| **Observation** | The model reflects on the response from the tool. |

This is essentially a **while loop** driven by a **system prompt** that defines:

- The agent's behaviour and rules
- The tools the agent has access to
- The Thought -> Action -> Observation cycle
- The termination condition (objective fulfilled)

The **ReAct cycle** (Reasoning + Acting) empowers agents to solve complex tasks iteratively — reasoning about tasks, utilizing tools, and continuously refining output based on feedback.

---

### Thoughts

Thoughts represent the agent's **internal reasoning and planning** processes. The agent uses its LLM capacity to analyze information — essentially its *inner monologue* as it works through a problem.

Agents can break down complex problems into smaller, manageable steps.

**Types of thoughts:**

| Type | Purpose |
|------|---------|
| Planning | Outlining steps to achieve a goal |
| Analysis | Examining data or context |
| Decision Making | Choosing between alternatives |
| Problem Solving | Working through obstacles |
| Memory Integration | Recalling relevant past context |
| Self-Reflection | Evaluating own reasoning |
| Goal Setting | Defining sub-objectives |
| Prioritization | Ordering tasks by importance |

#### Chain of Thought (CoT)

A prompting technique that guides a model to think through a problem **step-by-step** before producing a final answer.

- Helps the model reason internally without interacting with external tools.
- Triggered by prompts like: *"Let's think step by step."*
- **Best suited for**: Logic, math, and internal reasoning tasks.

#### ReAct: Reasoning + Acting

Combines **Reasoning** (Think) with **Acting** (Act). The model thinks step by step and interleaves actions (tool use) between reasoning steps.

- **Best suited for**: Information-seeking and dynamic multi-step tasks.

---

### Actions

Actions are the concrete steps an AI agent takes to interact with its environment.

#### Agent Action Types

| Type | Description |
|------|-------------|
| **JSON Agent** | The action to take is specified in JSON format. |
| **Code Agent** | The agent writes a code block that is interpreted externally. |
| **Function Calling Agent** | A subcategory of JSON Agent, fine-tuned to generate a new message for each action. |

#### Categories of Actions

| Category | Examples |
|----------|---------|
| **Information Gathering** | Web searches, database queries, document retrieval |
| **Tool Usage** | API calls, calculations, code execution |
| **Environment Interaction** | Manipulating digital interfaces or controlling physical devices |
| **Communication** | Engaging with users via chat or collaborating with other agents |

> **Important**: The LLM only handles text — it *describes* the action and parameters for a tool. For an agent to work properly, the LLM must **stop generating tokens** after emitting a complete action definition. This passes control back to the agent and ensures the result is parseable (JSON, code, or function-call format).

#### The Stop and Parse Approach

A key method for implementing structured, predictable agent actions:

1. **Generate in a structured format** — The agent outputs its intended action in a clear, predetermined format (JSON or code).
2. **Halt further generation** — The LLM stops generating additional tokens once the action is fully defined, preventing extra or erroneous output.
3. **Parse the output** — An external parser reads the formatted action, determines which tool to call, and extracts the required parameters.

> **Security Note**: Executing LLM-generated code may pose security risks, from prompt injection to the execution of harmful code. Always validate and sandbox generated code.

Actions bridge an agent’s internal reasoning and its real world interactions by executing clear, structured tasks whether through JSON, code, or function calls

---

### Observations

Observations are how an agent **perceives the consequences of its actions**. After executing a tool, the agent reviews the returned result and uses it to inform the next iteration of the Thought -> Action -> Observation loop.

Essentially signals from the enviroment: They provide crucial information that fuels the Agent’s thought process and guides future actions.

The agent:

- **Collects Feedbac**k: Receives data or confirmation that its action was successful (or not).
- **Appends Results**: Integrates the new information into its existing context, effectively updating its memory.
- **Adapts its Strategy**: Uses this updated context to refine subsequent thoughts and actions.

- This iterative incorporation of feedback ensures the agent remains dynamically aligned with its goals, constantly learning and adjusting based on real-world outcomes

| Type of Observation | Examples |
|----------|---------|
| **System Feedback** | Error messages, success notifications, status codes |
| **Data Changes** | Database updates, file system modifications, state changes |
| **Environmental Data** | Sensor readings, system metrics, resource usage |
| **Response Analysis** | API responses, query results, computation outputs |
| **Time-based Events** | Deadlines reached, scheduled tasks completed |

**Results are appended thorugh**:

- Parse the action to identify the function(s) to call and the argument(s) to use.
- Execute the action.
- Append the result as an Observation.

---

## Further Reading

<!-- TODO: Add links to related resources, tutorials, or next steps -->
