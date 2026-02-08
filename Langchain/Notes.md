# Foundation: Introduction to LangChain - Python

## Module 1: create agent

- Agents : piece of software that can percieve its enviroment and react. So reasonts and takes action

## Module 2: Advanced agents

- MCP : Open protocol that standardises how LLM applications work with your tools and data source
- E.G. Like USB
- MCP Host: Agent
- MCP Client
- MCP Server: Tools, Resources, Prompt
- can provide context to agent. But must call context as tool to allow agent to acess context, as it isnt actually passed to the model directly
- Done through tool runtime
- Agent state makes it mutable. Using checkpointing
- Adding value to custom state

### Multi Agent System

- longer the task is the worse the agent performance
- Quality sufffers
- Multi agent system can break this down
- Supervisor , Sub model -> uses singular orchestrator
- Add agents as tools for main agent

### Middleware

- catch all term
- functions we can insert in the loop to controll agent
- Key to levelup agent to production
- Basically guardrails
- E.G. long cpnversation
  - can summarise : summarise is an out of the box middleware function that can import
  - Or trim
- Human in the loop: approving sensitive actions, debugging , missing context
- Middle ware can be invoked befor or after agent call
- Node style middle ware is really good for hoping in and changing state
  - wrap style middle ware
  - can change models mid convo, or add specialised tools
- **Wrap style middleware**: Model request to access info
  - Adjust an agents tools, prompts, model while running
  - E.G. Giving an agent acessss to tools if user is internal
- **Node style middleware**: State + runtime changes.
  - Hooking into
  - Adjust an agent state while running
  - E.G. Trimming messages from long conversations
- **Tool calls middleware**: Tool runtime
  - Agent adjust its own state or retrieves runtime context
  - E.G. Updating the state with the username when provided to the Agent

## Agent chat UI

- UI 
- use https://agentchat.vercel.app/
- Make sure to add asyn and awai to wrap stle middleware functions