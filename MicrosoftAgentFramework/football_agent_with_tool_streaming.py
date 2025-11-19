from dotenv import load_dotenv
import os
import json
import asyncio
import httpx
from azure.identity import AzureCliCredential,DefaultAzureCredential
from pydantic import Field
from agent_framework.azure import AzureOpenAIResponsesClient, AzureOpenAIChatClient
from typing import Annotated
from pydantic import Field
from agent_framework import TextContent, FunctionCallContent, FunctionResultContent

load_dotenv() # Load environment variables from .env file
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_AI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_AI_CHAT_DEPLOYMENT_NAME")

# define a function (tool) to list football leagues
async def get_football_leagues() -> str:
    """Get a list of all available football leagues."""
    print("⚽ Fetching all football leagues...")
    
    url = "https://api-football-standings.azharimm.site/leagues"
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status"):
                leagues = data.get("data", [])
                league_list = [f"{league['name']} ({league['abbr']}) - ID: {league['id']}" 
                              for league in leagues[:10]]  # Limit to first 10
                return "Available Leagues:\n" + "\n".join(league_list)
            else:
                return "Could not fetch leagues data."
    except Exception as e:
        return f"Error fetching leagues: {str(e)}"

async def get_league_detail(
    league_id: Annotated[str, Field(description="The league ID (e.g., 'eng.1' for Premier League)")]
) -> str:
    """Get details about a specific football league."""
    print(f"⚽ Fetching details for league {league_id}...")
    
    url = f"https://api-football-standings.azharimm.site/leagues/{league_id}"
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status"):
                league = data.get("data", {})
                return f"League: {league.get('name')} ({league.get('abbr')})\nSlug: {league.get('slug')}"
            else:
                return f"Could not fetch details for league {league_id}."
    except Exception as e:
        return f"Error fetching league details: {str(e)}"


async def get_league_standings(
    league_id: Annotated[str, Field(description="The league ID (e.g., 'eng.1' for Premier League)")],
    season: Annotated[int, Field(description="The season year (e.g., 2020 for 2020-2021 season)")] = 2021,
    sort: Annotated[str, Field(description="Sort order: 'asc' or 'desc'")] = "asc"
) -> str:
    """Get football league standings for a specific season."""
    print(f"⚽ Fetching standings for league {league_id}, season {season}...")
    
    url = f"https://api-football-standings.azharimm.site/leagues/{league_id}/standings"
    params = {
        "season": season,
        "sort": sort
    }
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client: 
            response = await client.get(url, params=params)
            print(f"Status Code: {response.status_code}")  # DEBUG
            #print(f"Response: {response.text[:500]}")  # DEBUG - first 500 chars
            # Check if response is JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                return f"API returned non-JSON response. The API may be temporarily unavailable."
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("status"):
                standings_data = data.get("data", {})
                league_name = standings_data.get("name")
                season_display = standings_data.get("seasonDisplay")
                standings = standings_data.get("standings", [])
                
                if not standings:
                    return f"No standings available for {league_name} - {season_display}"
                
                # Format top 10 teams
                result = f"{league_name} - {season_display} Standings:\n"
                for idx, team in enumerate(standings[:10], 1):
                    stats = team.get("stats", [{}])[0]
                    team_name = team.get('team', {}).get('displayName', 'Unknown')
                    points = stats.get('points', 'N/A')
                    result += f"{idx}. {team_name} - {points} pts\n"
                # for team in standings[:10]:
                #     stats = team.get("stats", [{}])[0]
                #     result += f"{team.get('team', {}).get('displayName')} - Points: {stats.get('points', 'N/A')}\n"
                
                return result
            else:
                return f"Could not fetch standings for league {league_id}."
    except httpx.TimeoutException:
        return f"Request timed out while fetching standings for {league_id}."
    except Exception as e:
        return f"Error fetching standings: {str(e)}"
        
# initialise a chat agent with azure openai response and a toolset
agent = AzureOpenAIChatClient(
         endpoint=AZURE_OPENAI_ENDPOINT,
         api_key=AZURE_OPENAI_KEY,
         deployment_name=AZURE_OPENAI_DEPLOYMENT
).create_agent(
        model=AZURE_OPENAI_DEPLOYMENT,
        name="weather-agent",
        instructions="You are a helpful agent that responds to user queries.",
        tools=[ get_football_leagues, get_league_detail, get_league_standings] 
)

async def main():
   
#    result = await agent.run("Hello, can you tell me the current football league standings for the Premier League?")
#    print("\n🤖 Agent Response:")
#    print(result)

    # code to run as a stream 
    async for update in agent.run_stream("Hello, can you tell me the football league standings for the Premier League 2020 season?"):
        #print(f"Content count: {len(update.contents)}")
        #print(f"update type: {type(update)}")
        if update.text:
            print(update, end='', flush=True)

    # async for update in agent.run_stream("Hello, can you tell me the current football league standings for the Premier League?"):
    #     for content in update.contents:
    #         print(f"Content type: {type(content)}")
    #         if isinstance(content, TextContent):
    #             print(f"Text : {content.text}")
    #         elif isinstance(content, FunctionCallContent):
    #             print(f"function call: {content.name}")
    #             print(f"Call ID: {content.call_id}")
    #             print(f"Arguments: {content.arguments}")
    #         elif isinstance(content, FunctionResultContent):
    #             print(f"Function results: {content.result}")


if __name__ == "__main__":
    asyncio.run(main())
