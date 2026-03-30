# Travel agent, Venue, Dj , coordinator
from typing_extensions import runtime
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.chat_models import init_chat_model
from pprint import pprint
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver  
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import tool
from typing import Dict, Any
from langchain.agents import AgentState
from langchain.tools import ToolRuntime
from langchain.messages import HumanMessage, ToolMessage
from langgraph.types import Command

class WeddingState(AgentState):
    origin: str
    destination: str
    guest_count: str
    genre: str


load_dotenv()

# Online MCP configuration
client = MultiServerMCPClient(
    {
        "time": {
            "transport": "stdio",
            "command": "uvx",
            "args": [
                "mcp-server-time",
                "--local-timezone=America/New_York"
            ]
        }
    },
    {
        "mcpServers": {
            "playwright": {
            "command": "npx",
            "args": [
                "@playwright/mcp@latest"
        ]
        }
    }
    },
    {
        "mcpServers": {
            "search1api": {
            "command": "npx",
            "args": [
                "-y",
                "search1api-mcp"
            ],
            "env": {
                "SEARCH1API_KEY": "YOUR_SEARCH1API_KEY"
            }
            }
        }
        },
        {
            "mcpServers": {
                "google-maps": {
                "command": "docker",
                "args": [
                    "run",
                    "-i",
                    "--rm",
                    "-e",
                    "GOOGLE_MAPS_API_KEY",
                    "mcp/google-maps"
                ],
                "env": {
                    "GOOGLE_MAPS_API_KEY": "<YOUR_API_KEY>"
                }
                }
            }
            },
            {
                travel_server": {
                "transport": "streamable_http",
                "url": "https://mcp.kiwi.com"
    }
)

# get tools
tools = await client.get_tools()

# initialise a model, with customization
gpt_model = init_chat_model(
    model="gpt-5-nano",
    # Kwargs passed to the model:
    temperature=1.0
    )

# create master prompt
Master_prompt = """
 You are a wedding coordinator. Delegate tasks to your specialists for flights, venues and playlists.
First find all the information you need to update the state. Once that is done you can delegate the tasks.
Once you have received their answers, coordinate the perfect wedding for me.

You have access to the following tools:
1. A search tool to search for venues, DJs, coordinators etc. in a specific
location and get details about them.
2. A google maps tool to get directions and travel time between locations.
3. A time tool to check for availability of venues, DJs, coordinators etc. on specific dates.
4. An annual income calculator tool to calculate the annual income of a person based on their salary.
5. A wedding budget calculator tool to calculate the wedding budget of a person based on their monthly income, monthly expenses, number of months engaged, existing savings and family contributions.
6. A per head allocation calculator tool to calculate the per head allocation for a wedding based on the total budget and number of guests.
"""

tavily_client = TavilyClient()

@tool
def web_search(query: str) -> Dict[str, Any]:

    """Search the web for information"""

    return tavily_client.search(query)

# annual income tool
@tool
def annual_income(salary: float) -> float:
    """Calculate the annual income of a person based on their salary."""
    return salary * 12
# wedding budget too; (Combined Monthly Income - Monthly Expenses) × Number of Months Engaged + Existing Savings + Family Contributions.
@tool
def wedding_budget(monthly_income: float, monthly_expenses: float, months_engaged: int, existing_savings: float, family_contributions: float) -> float:
    """Calculate the wedding budget of a person based on their monthly income, monthly expenses, number of months engaged, existing savings and family contributions."""
    return (monthly_income - monthly_expenses) * months_engaged + existing_savings + family_contributions
# a per head allocation tool; Budget per Guest = Total Budget / Number of Guests.
@tool
def per_head_allocation(total_budget: float, number_of_guests: int) -> float:
    """Calculate the per head allocation for a wedding based on the total budget and number of guests."""
    return total_budget / number_of_guests

flight_prompt = """
You are a travel Agent
You are a helpful assistant who can search for flights to and from various locations and get details about them
You are not allowed to ask any more follow up questions, you must find the best flight options based on the following criteria:
    - Price (lowest, economy class)
    - Duration (shortest)
    - Date (time of year which you believe is best for a wedding at this location)
    To make things easy, only look for one ticket, one way.
    You may need to make multiple searches to iteratively find the best options.
    You will be given no extra information, only the origin and destination. It is your job to think critically about the best options.
    Once you have found the best options, let the user know your shortlist of options.
You have access to the following tools:
1. A search tool to search for flights to and from various locations and get details about them
"""

venue_prompt = """
You are a Venue Agent
You are a helpful assistant who can search for venues in various locations and get details about them
You are not allowed to ask any more follow up questions, you must find the best venue options based on the following criteria:
    - Price (lowest)
    - Capacity (exact match)
    - Reviews (highest)
    You may need to make multiple searches to iteratively find the best options.
You have access to the following tools:
1. A search tool to search for venues in various locations and get details about them
"""

dj_prompt = """
You are a DJ Agent
You are a helpful assistant who can search for DJs in various locations and get details about them
Once you have your playlist, calculate the total duration and cost of the playlist, each song has an associated price.
    If you run into errors when querying the database, try to fix them by making changes to the query.
    Do not come back empty handed, keep trying to query the db until you find a list of songs.
    You may need to make multiple queries to iteratively find the best options.
You have access to the following tools:
1. A search tool to search for DJs in various locations and get details about them
"""

# create flights sub agent
flight_agent = create_agent(model = gpt_model,
                     system_prompt=flight_prompt,
                     tools = tools,
                     checkpointer=InMemorySaver(),
)
# create venue sub agent
venue_agent = create_agent(model = gpt_model,
                        system_prompt=venue_prompt,
                        tools = tools,
                        checkpointer=InMemorySaver(),
)   
# create DJ sub agent
dj_agent = create_agent(model = gpt_model,
                        system_prompt=dj_prompt,
                        tools = [web_search],
                        checkpointer=InMemorySaver(),
)

# tools to call flight agent
@tool
def call_flight_agent(runtime: ToolRuntime, query: str) -> str:
    """Travel agent searches for flights to the desired destination wedding location."""
    origin = runtime.state["origin"]
    destination = runtime.state["destination"]
    response = flight_agent.invoke({"messages": [HumanMessage(content=query)]})
    return response["messages"][-1].content
# tool to call venue agent
@tool
def call_venue_agent(runtime: ToolRuntime) -> str:
   """Venue agent chooses the best venue for the given location and capacity."""
   destination = runtime.state["destination"]
   capacity = runtime.state["guest_count"]
   query = f"Find wedding venues in {destination} for {capacity} guests"
   response = venue_agent.invoke({"messages": [HumanMessage(content=query)]})
   return response["messages"][-1].content
# tool to call DJ agent
@tool
def call_dj_agent(runtime: ToolRuntime) -> str:
    """Playlist agent curates the perfect playlist for the given genre."""
    genre = runtime.state["genre"]
    query = f"Find {genre} tracks for wedding playlist"
    response = dj_agent.invoke({"messages": [HumanMessage(content=query)]})
    return response["messages"][-1].content
@tool
def update_state(origin: str, destination: str, guest_count: str, genre: str, runtime: ToolRuntime) -> str:
    """Update the state when you know all of the values: origin, destination, guest_count, genre"""
    return Command(update={
        "origin": origin, 
        "destination": destination, 
        "guest_count": guest_count, 
        "genre": genre, 
        "messages": [ToolMessage("Successfully updated state", tool_call_id=runtime.tool_call_id)]}
        )

# create master agent with system prompt and tools, using checkpointer to save the agent's memory in the InMemorySaver which is a simple in-memory storage for checkpoints.
master_agent = create_agent(model = gpt_model,
                     system_prompt=Master_prompt,
                     tools=[call_flight_agent, call_venue_agent, call_dj_agent, annual_income, wedding_budget, per_head_allocation],
                     checkpointer=InMemorySaver(),
                     state_schema=WeddingState
)

while True:
    question = input("Please enter your wedding planning query: ")

    # Config for thread id
    config = {"configurable": {"thread_id": "1"}}

    response = master_agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config,
        )
    print(response["messages"][-1].content)