# MCP

## Key word

Agent:

- React: Reason + Act

Workflows

- steps to give instructions to agent

MCP

- standard way for AI models to connecct in consistent, secure and reusable manner
- to inspect run ```npx @modelcontextprotocol/inspector```
- SSE: Server Sent events
- For workflow you need to
  - Convert worflow to agent
  - convert agent to tool
  - create wrapper agent using tool
  - expose wrapper agent as MCP server