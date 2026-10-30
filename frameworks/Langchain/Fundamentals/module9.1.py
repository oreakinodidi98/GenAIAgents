from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from random import randint
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import asyncio
# mcp
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
import httpx
from markdownify import markdownify
from langsmith import traceable

from IPython.display import Markdown, display

import langsmith.utils as lsu
# LangSmith caches env lookups; clear cache when setting vars inside a running notebook
lsu.get_env_var.cache_clear()

from dotenv import load_dotenv
load_dotenv()

# Interceptors for handling tool call retries and fallbacks
async def retry_interceptor(
    request: MCPToolCallRequest,
    handler,
    max_retries: int = 3,
    delay: float = 1.0,
):
    """Retry failed tool calls with exponential backoff."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return await handler(request)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)  # Exponential backoff
                print(f"Tool {request.name} failed (attempt {attempt + 1}), retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
    raise last_error

# Interceptor for handling tool call fallbacks
async def fallback_interceptor(
    request: MCPToolCallRequest,
    handler,
):
    """Return a fallback value if tool execution fails."""
    try:
        return await handler(request)
    except TimeoutError:
        return f"Tool {request.name} timed out. Please try again later."
    except ConnectionError:
        return f"Could not connect to {request.name} service. Using cached data."

# Connect to the remote MCP server, specifying the URL and transport method, and attach tool interceptors for retries and fallbacks
mcp_client = MultiServerMCPClient(
    {
        "microsoft-learn": {
            "url": f"https://{app_service_mcp_server_open_web_search_fqdn}/mcp",
            "transport": "http",
        }
    },
    tool_interceptors=[retry_interceptor, fallback_interceptor]
)

# Tool to fetch and convert webpage content to markdown
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

    
async def main():
    # Test environment variables
    print("endpoint:", os.getenv("FOUNDRY_ENDPOINT"))
    print("deployment:", os.getenv("LLM_MODEL_DEPLOYMENT_NAME"))
    print("langsmith project:", os.getenv("LANGSMITH_PROJECT"))
    print("langsmith endpoint:", os.getenv("LANGSMITH_ENDPOINT"))
    print("langsmith tracing:", os.getenv("LANGSMITH_TRACING"))
    print("langsmith tracing v2:", os.getenv("LANGSMITH_TRACING_V2"))
    print("langsmith API Key:", os.getenv("LANGSMITH_API_KEY"))


    # initialise model
    print(f"\ninitialising model...")
    model = ChatOpenAI(
        base_url=f"{os.getenv('FOUNDRY_ENDPOINT')}/openai/v1",
        #api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        api_key=get_bearer_token_provider(
            DefaultAzureCredential(), 
            "https://ai.azure.com/.default"
            ),
        model=os.getenv('LLM_MODEL_DEPLOYMENT_NAME'),
        streaming=True
    )
    print(f"\nmodel initialised.")

    # Show tools exposed by Microsoft Learn and assign them to the agent through the tools parameter
    mcp_tools = await mcp_client.get_tools()
    print(f"\n MCP tools: {[t.name for t in mcp_tools]}")
    
    print(f"\ncreating agent...")

    # Create a subagent
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

    # Wrap it as an async tool so it stays in the async execution path
    @tool(description="Fetch a webpage and return markdown content")
    @traceable
    async def call_sub_agent(query: str):
        result = await subagent.ainvoke({"messages": [{"role": "user", "content": query}]})
        return result["messages"][-1].content

    # Main agent with subagent as a tool
    main_agent = create_agent(model=model, 
                            tools=[*mcp_tools, call_sub_agent],     
                            system_prompt=(
    """"
    You are the Main Research Orchestrator.
    Goal: answer the user query by coordinating web discovery and parallel subagent summarization.
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
        {"messages": [HumanMessage(content=
        """
            What are the latest open LLM models in 2026 ?
            Compare their capabilities and limitations.
            Precise how many parameters each model has and the size of their input context window and the date of release.
            Search the web for 50 result pages. Fetch webpages.
            Cite your references in the response at the end.
        """
        )]},
        stream_mode="values",
    ):
        step["messages"][-1].pretty_print()
        last_message = step["messages"][-1]

    # show the response content as markdown
    content = getattr(last_message, "content", "")
    if isinstance(content, list):
        markdown_text = "\n".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    else:
        markdown_text = str(content)


    display(Markdown(markdown_text))

if __name__ == "__main__":
    asyncio.run(main())