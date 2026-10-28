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
import httpx
from markdownify import markdownify



from dotenv import load_dotenv
load_dotenv()

# Connect to the Microsoft Learn MCP server, public endpoint so no authentication is required
mcp_client = MultiServerMCPClient(
    {
        "microsoft-learn": {
            "url": f"https://{app_service_mcp_server_open_web_search_fqdn}/mcp",
            "transport": "http",
        }
    }
)

# Tool to fetch and convert webpage content to markdown
@tool
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
        streaming=True,
        max_completion_tokens=512
    )
    print(f"\nmodel initialised.")
    
    print(f"\ngetting response from model...")
    # get response from model
    response = model.stream([HumanMessage(content="Tell me about yourself.")])

    # print response chunks as they arrive
    for chunk in response:
        print(chunk.content, end="", flush=True)

    # Show tools exposed by Microsoft Learn and assign them to the agent through the tools parameter
    mcp_tools = await mcp_client.get_tools()
    print(f"\n MCP tools: {[t.name for t in mcp_tools]}")
    
    print(f"\ncreating agent...")
    # create agent with the llm model
    learn_agent = create_agent(
        model=model,
        tools=[*mcp_tools, fetch_webpage_content],
        middleware=[],
        checkpointer=None,
    )

    # ask agent question 
    async for step in learn_agent.astream(
        {"messages": [HumanMessage(content=
        """
        What are the latest open and close LLM models in 2026 ?
        Compare their capabilities and limitations.
        Search the web for 50 result pages. Fetch webpages.
        Cite your references in the response at the end.
        """
        )]},
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

if __name__ == "__main__":
    asyncio.run(main())