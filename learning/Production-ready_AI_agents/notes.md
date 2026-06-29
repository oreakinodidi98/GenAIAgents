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
  - [Langchain fundamentals](#langchain-fundamentals)
  - [Tools and Function Calling](#tools-and-function-calling)

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

## Langchain fundamentals

React Agent: Reason and act. Runs in a loop. Agent has a thought about what to do, takes an action by calling the tool and reads observation/result
if a task is not done it loops back 
onse ansered it stops
so repeats over and over until it solves problem 

Demo 

1. Use terraform to deploy LLM in Azure AI foundry
2. Get endpoint and KEy
3. Configure the client
4. Build a ReAct Agent


## Tools and Function Calling