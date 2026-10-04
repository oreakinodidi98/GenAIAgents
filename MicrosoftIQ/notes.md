# Microsoft IQ

## Overview

- I have an AI model.
- It is trained on public knowledge.
- It has no information about my enterprise or internal data.
- To leverage AI capabilities with agents, I need to feed the model additional enterprise information.
- The higher the relevance of that data, the better the AI response.
- The model essentially needs additional enterprise context.
- Microsoft IQ unifies an organization’s flow of work, operations, and knowledge into one shared, trusted intelligence layer
- Even the most advanced AI agents today lack a unified, complete understanding of the organizations they support.
- This addresses a fundamental gap in enterprise AI.

### Goal

- Get AI agents to the same level of knowledge as your best employee.
- Provide trusted enterprise knowledge and context.
- Build complete enterprise context so agents can interact at a human-like level of understanding.

## M365 and D365 (WorkIQ)

WorkIQ represents work-pattern and productivity context from Microsoft 365 and Dynamics 365.

Data signals include:

- Messages.
- Documents.
- Customer signals.
- A semantic index on top of Microsoft Graph API.
- Natural language retrieval to find the most relevant information.

### WorkIQ capabilities

- Adds memory and personalization.
- Learns how you work, communicate, structure your day, what you care about, and your objectives.
- Creates actions based on your rhythm of work.
- Learns company-wide processes.
- semantic index- M365 content (word documents, calendar, email etc )
- Uses tuned inferencing capabilities.
- Improves interaction quality across data, apps, and workflows.
- Work IQ connects AI to how employees work across the organization.
- It synthesizes signals from people, documents, emails, meetings, and workflows to maintain continuity as work changes, so Copilot and agents understand what is active, who is involved, and what needs attention now.


## Institutional Knowledge

Institutional knowledge can live in document stores, websites, and curated enterprise repositories.

- This can be in a store or another website.
- You can use a highly curated set of searches to find the most relevant information.

### FoundryIQ

FoundryIQ is a curated, AI-powered knowledge and search layer for agents.

- Strict, curated AI-powered search and knowledge for agent use.
- Curated information sources.
- Examples: Blob storage, SharePoint, unstructured data from OneLake, and trusted web sources.
- Granular control of which knowledge sources are included in the knowledge base.
- Agents can be constrained to use only these approved sources.
- AI selects the right pieces of information from those sources.
- In Foundry, this is configured through knowledge sources.
- Provides a high level of control over what the agent can use.
- Supports institutional knowledge bases.

## Fabric

Fabric represents enterprise operational and analytical data context.

- OneLake with many data types.
- Analytical and operational data.
- Streaming data.
- Native SQL.
- Massive data in OneLake, but not always easy to map semantically.
- A key question is how data relates to enterprise entities and business rules.

### FabricIQ

FabricIQ adds semantic understanding on top of Fabric and OneLake data.

- Defines entities and relationships between entities and rules that impact operations.
- Adds a semantic layer on top of data in OneLake.
- Creates operational intelligence that can be leveraged by agents.

## Core Challenge

The challenge today is that organizations have a lot of great information, but it is not always usable by AI as enterprise knowledge.

- This limits the capability of AI agents.
- Your best employee understands this data and knows how to use it.

## Microsoft IQ as a Unified Context Layer

All of the above together make up Microsoft IQ, so the agent has context from all three domains to perform its job.

Example combined context:

- Emails, messages, and meetings.
- Contracts and institutional documents.
- Business state and operational data.

Microsoft IQ is not a single feature, it is built from four powerful, complementary IQ elements. Together, they form the engine that gives agents true awareness of your people, your business, and your knowledge–including the world's knowledge.


## Where It Is Consumed

Microsoft IQ can be consumed from multiple agent-building surfaces:

- Agent Builder (low code).
- Copilot Studio (low code).
- Foundry (pro code).
- Other platforms and custom implementations.

Wherever I build my agents, they can interact with Microsoft IQ.

- Access can happen through MCP or APIs.
- Not just for information retrieval, but also for actions.
- Enables a unified data plane and control plane.

## Governance and Security Plane

Agent 365-style enterprise control stack includes:

- Entra ID.
- Purview.
- Defender for threat protection.
- Agent registry.
- Governance and protection controls.