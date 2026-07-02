import os
import asyncio
import json
from dotenv import load_dotenv
from pydantic import SecretStr
from azure.identity import AzureCliCredential
# For LangSmith tracing
import langsmith.utils as lsu

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
import httpx
from langchain.tools import tool
from langsmith import traceable
from markdownify import markdownify

# load environment variables from .env file
load_dotenv()

# Create an Azure CLI credential 
credential = AzureCliCredential(process_timeout=30)

# function to test if environment variables are set
def require_env(name: str) -> str:
    """Return a required environment variable or fail fast with a clear message."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

# retrieve required environment variables
llm_model_deployment_name = require_env('LLM_MODEL_DEPLOYMENT_NAME_CHATGPT')
foundry_api_key = require_env('FOUNDRY_API_KEY')
foundry_endpoint = require_env('FOUNDRY_ENDPOINT')
aca_mcp_server_open_web_search_fqdn = require_env('ACA_MCP_SERVER_OPEN_WEB_SEARCH_FQDN')
langsmith_endpoint = require_env('LANGSMITH_ENDPOINT')
# langsmith_project = require_env('LANGSMITH_PROJECT_NAME')
langsmith_project = "subagents-GenAI-Agents"  


# Set up LangSmith Tracing

print("LangSmith tracing enabled:", lsu.tracing_is_enabled())
print("LangSmith endpoint:", langsmith_endpoint)
print("LangSmith project:", langsmith_project)


# Connect to the LLM endpoint hosted on Foundry
model = ChatOpenAI(
    base_url=f"{foundry_endpoint}/openai/v1",
    api_key=SecretStr(foundry_api_key),
    model=llm_model_deployment_name,
    streaming=True # streaming to get output as it is written by llm
   # max_completion_tokens=512 # specified limit to 512
)

# Connect to the MCP server by creating an MCP client
# Use MultiServerMCPClient to connect to the MCP server over Streamable HTTP transport
# Client automatically discovers all tools the server exposes and makes them available as LangChain tools
mcp_client = MultiServerMCPClient(
    {
        "web-search": {
            "url": f"https://{aca_mcp_server_open_web_search_fqdn}/mcp",
            "transport": "http",
        }
    }
)

# A tool to fetch webpage content and convert HTML to markdown. This tool can be used by the agent to retrieve and process web content.
@tool
@traceable
def fetch_webpage_content(url: str, timeout: float = 10.0) -> str:
    """Fetch webpage and convert HTML to markdown."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = httpx.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return markdownify(response.text)
    except Exception as e:
        return f"Error fetching {url}: {e!s}"

# Test the agent with a simple question that requires reasoning and tool usage.
question = (
    "What are the latest open and closed-source LLM models in 2026 ?\n"
    "Compare their capabilities and limitations.\n"
    "Search the web sequentially, inspect a reasonable number of high-quality sources, and fetch relevant webpages.\n"
    "Do not issue a tool call unless you have valid arguments for it.\n"
    "Cite your references at the end of the response."
)

# Subagent
subagent = create_agent(model=model, 
                            tools=[fetch_webpage_content],
                            system_prompt=(
    """"
    You are a URL-focused Research Subagent.
    You receive exactly:
    one url
    one user_query
    Available tool:
    fetch_webpage_content(url) to retrieve page content.
    Task:
    Fetch the page content for the provided URL.
    Extract only information relevant to user_query.
    Produce a concise, faithful summary grounded in that page only.
    Rules:
    Do not browse other URLs.
    Do not add outside knowledge.
    If the page is inaccessible or irrelevant, return that clearly.
    Prefer concrete facts, definitions, numbers, dates, and claims tied to page text.
    """
    ))

# Wrap subagent as an async tool so it stays in the async execution path.
# Contract: one URL plus the original user query.
@tool(description="Summarize one URL for the given user query. Inputs: url, user_query.")
@traceable
async def call_sub_agent(url: str, user_query: str):
    result = await subagent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"url: {url}\n"
                        f"user_query: {user_query}\n"
                        "Fetch the page and summarize only information relevant to user_query."
                    ),
                }
            ]
        }
    )
    return result["messages"][-1].content

# Stream agent execution asynchronously and print the latest agent response.
async def run_agent() -> None:
    # Discover tools exposed (async call must be inside async function).
    mcp_tools_web_search = await mcp_client.get_tools()
    print("MCP tools Discovered:", [t.name for t in mcp_tools_web_search])

    # Find the tool called "search" by name
    search_tool = next(t for t in mcp_tools_web_search if t.name == "search")

    # invoke the search tool and inspect the raw result returned by the MCP server
    result = await search_tool.ainvoke(
    {
        "query": "What are the latest LLM models by Google?", 
        "limit": 20, 
        "engines": ["duckduckgo"]
    })

    # result is already a list — extract the "text" field and parse it
    data = json.loads(result[0]["text"])
    print(json.dumps(data, indent=4))

    # Create an agent with the remote search tool and the local fetch_webpage_content tool.
    agent_tools = [search_tool, call_sub_agent]
    # The agent will reason about when to search the web, fetch pages, and synthesize a final answer with citations.
    main_agent = create_agent(
        model=model.bind_tools(agent_tools, parallel_tool_calls=True),
        tools=agent_tools,
        system_prompt=(
        """"
        You are the Main Research Orchestrator.
        Goal: answer the user query by coordinating web discovery and subagent summarization.
        Available tools:
        search_tool(query): finds relevant websites.
        call_sub_agent(url, user_query): sends one URL and the original query to a subagent and gets back a structured summary.
        Required workflow:
        Understand the user query and identify intent, scope, and key entities.
        Use search_tool to find high-quality candidate URLs.
        Select the number of diverse, relevant websites (skip duplicates, low-signal pages, ads, login walls when possible).
        If not mentioned, default to 3–6 websites.
        For each selected URL, call call_sub_agent(url, user_query).
        Merge returned summaries into one synthesized response.
        Resolve conflicts by noting disagreement and preferring clearer, better-supported sources.
        Rules:
        Do not invent facts not present in subagent outputs.
        If tools fail, continue with successful results and state limitations.
        Keep reasoning concise and focus on user value.
        Final response format:
        Short answer
        Key findings (bullet list)
        What sources say (1 bullet per URL)
        Gaps / uncertainty
        Sources (list of URLs)
        """
    ))

    last_message = None

    async for step in main_agent.astream(
        {"messages": [HumanMessage(content=question)]},
        stream_mode="values"
    ):
        # Output has two sections: the human message and the agent response.
        # Print the latest message, which is the agent response.
        step["messages"][-1].pretty_print()
        last_message = step["messages"][-1]
    
    # Print the final response content as plain text for terminal runs.
    content = getattr(last_message, "content", "")
    if isinstance(content, list):
        markdown_text = "\n".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    else:
        markdown_text = str(content)

    print("\nFinal response:\n")
    print(markdown_text)

if __name__ == "__main__":
    asyncio.run(run_agent())