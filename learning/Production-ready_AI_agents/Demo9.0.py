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
langsmith_project = require_env('LANGSMITH_PROJECT_NAME')


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

# test if agent can be created and run with the LLM model
# Done by invoking model with test prompt and stream the output
# prompt = "tell me about your self"
# response = model.stream([HumanMessage(content=prompt)])

# # print the streamed response
# for chunk in response:
#     print(chunk.content, end="", flush=True)

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
    "I am building a high-scale, privacy-focused customer support automation platform. I need you to research the top 3 open-source and top 3 closed-source LLMs currently available in July 2026.\n\n"
    "Create a comparative decision matrix for me that balances: (1) Reasoning capability on complex multi-step workflows, (2) Cost-per-million-tokens, (3) Data privacy/compliance risks, and (4) Context window limitations.\n\n"
    "Finally, recommend a 'hybrid' architecture where I use a larger frontier model for edge-case reasoning and a smaller/local model for routine tasks. Justify your choice based on current latency and cost data."
)

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
    print("\n=== MCP SEARCH SANITY CHECK (RAW TOOL OUTPUT) ===")
    print(json.dumps(data, indent=4))
    print("=== END SANITY CHECK ===\n")

    # Create an agent with the remote search tool and the local fetch_webpage_content tool.
    agent_tools = [search_tool, fetch_webpage_content]
    # The agent will reason about when to search the web, fetch pages, and synthesize a final answer with citations.
    agent_with_mcp = create_agent(
        model=model.bind_tools(agent_tools, parallel_tool_calls=False),
        tools=agent_tools
    )

    last_message = None

    async for step in agent_with_mcp.astream(
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