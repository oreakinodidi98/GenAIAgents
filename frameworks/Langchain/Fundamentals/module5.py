from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from random import randint
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import asyncio

# Import necessary libraries for HTTP requests and markdown conversion
import httpx
from markdownify import markdownify

# Import tools for Azure dynamic sessions (Python REPL and Bash)
from langchain_azure_dynamic_sessions.tools import SessionsPythonREPLTool
from langchain_azure_dynamic_sessions.tools import SessionsBashTool
# Initialize Azure CLI credential for authentication with Azure services
from azure.identity import AzureCliCredential
credential = AzureCliCredential()

from dotenv import load_dotenv
load_dotenv()

def access_token_provider():
    #token = credential.get_token("https://dynamicsessions.io/.default")
    token = get_bearer_token_provider(
            DefaultAzureCredential(), 
            "https://ai.azure.com/.default"
        )
    return token()


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
    print("Session Pool Managment Endpoint:", os.getenv("SESSION_POOL_MANAGEMENT_ENDPOINT"))
    print("MCP Session Pool Endpoint:", os.getenv("MCP_SESSION_POOL_ENDPOINT"))
    print("Session Pool Managment Endpoint (shell):", os.getenv("SESSION_POOL_MANAGEMENT_ENDPOINT_SHELL"))
    print("MCP Session Pool Endpoint (shell):", os.getenv("MCP_SESSION_POOL_ENDPOINT_SHELL"))

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
    response = model.stream([HumanMessage(content="Tell me about France.")])

    # print response chunks as they arrive
    for chunk in response:
        print(chunk.content, end="", flush=True)

   # get the management endpoint from the session pool in the Azure portal
    toolPythonSession = SessionsPythonREPLTool(
        pool_management_endpoint=os.getenv("SESSION_POOL_MANAGEMENT_ENDPOINT"),
        access_token_provider=access_token_provider,
    )

    # get the management endpoint from the session pool in the Azure portal
    toolBashSession = SessionsBashTool(
        pool_management_endpoint=os.getenv("SESSION_POOL_MANAGEMENT_ENDPOINT_SHELL"),
        access_token_provider=access_token_provider,
    )

    print(f"\ncreating agent...")
    # create agent with the llm model
    agent = create_agent(
        model=model,
        tools=[toolPythonSession, toolBashSession, fetch_webpage_content],
        middleware=[],
        checkpointer=None,
    )
    
    # ask agent question 
    async for step in agent.astream(
        {"messages": [HumanMessage(content=
        """
        What is the current time in Nigeria and France ? 
        Use the python REPL tool to get the answer
        """
        )]},
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print()


    # ask agent question 
    async for step in agent.astream(
        {"messages": [HumanMessage(content=
        """
        Run the printenv shell command 
        To check enviroment vaiables of this sessions
        Also run curl ifconfig.me/ip in shell and provide output
        """
        )]},
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

    async for step in agent.astream(
        {"messages": [{
            "role": "user", 
            "content": """
                Create a hello world flask app in a new remote environment. 
                Then send a request to the app to show that it works.
            """
            }]},
        stream_mode="values",
    ):
        step["messages"][-1].pretty_print()


    async for step in agent.astream(
        {"messages": [{"role": "user", 
                    "content": """
                            Get the history of the Microsoft stock price for the last 5 years and plot it. 
                            Install the required packages in the session if needed.
                            save the chart as `msft_5y.png`.
                    """}]},
        stream_mode="values",
    ):
        step["messages"][-1].pretty_print()

if __name__ == "__main__":
    asyncio.run(main())