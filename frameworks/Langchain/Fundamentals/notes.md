# Langchain Fundamentals

## Introduction

- Agents : piece of software that can percieve its enviroment and react. So reasonts and takes action
- Framework: how you build the agents
- Provider: where the model actually runs

## Module1: Langchain Fundaments

- Set up IAC
- Terraform to deploy model
- Get endpoint & KEy
- Configure Client
- Build a ReAct Agent
- REACT= Reason + ACT -> Thought, Action , Observation and final answer

Need to create virtul enviroment . Use code
1. Set up Virtual enviroment ``python -m venv agent_env`` then ``agent_env\Scripts\activate``
2. Install needed packages `` pip install -r requirements.txt ``

## Module 2: tools and function calling

How ana agent calls a tool:

Define tool
Bind tool to the model
Control invocation
Agent decides

Model chooses the tool not you

How it really works
user asks questions
model decide a tool is needed a returns a tool call with arguments
app runs that tool
result headed back to model which is sued to write the final answer

this is a round trip

## Module 3: MCP

connecting agent to outside world
connect, discover toools exposed , run agent quaries , provides grounded answer

What is MCP

Open standard that connects agent (client) to a server that exposes tools, resources and prompts

## Module 4: Open Web search

remote MCP server over streamable HTTP
Remote MCP -> invoke tools -> intercept & error handling -> fetch pages

Local Vs remote way to run MCP server

Local uses stdio
perfect for demos and local mcp server
Agent connects to the server over stdio

remote
uaes streamable http
Agent connects to remote servere over streamable http
allows agent to call a hosted server over the network
scalable 
shared
no locall install
can layer interceptors for login and retries also can include custom tools
can host mcp server in azure app service