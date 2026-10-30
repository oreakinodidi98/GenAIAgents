from grpc import services
from huggingface_hub import login
import os
from dotenv import load_dotenv
from smolagents import CodeAgent, DuckDuckGoSearchTool, FinalAnswerTool, InferenceClientModel, load_tool, tool, VisitWebpageTool, Tool
import numpy as np
import time
import datetime

from langfuse import get_client
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

login(token=HF_TOKEN)
langfuse = get_client()


# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

SmolagentsInstrumentor().instrument()

# Tool to suggest a menu based on the occasion
@tool
def suggest_menu(occasion: str) -> str:
    """
    Suggests a menu based on the occasion.
    Args:
        occasion (str): The type of occasion for the party. Allowed values are:
                        - "casual": Menu for casual party.
                        - "formal": Menu for formal party.
                        - "superhero": Menu for superhero party.
                        - "custom": Custom menu.
    """
    if occasion == "casual":
        return "Pizza, snacks, and drinks."
    elif occasion == "formal":
        return "3-course dinner with wine and dessert."
    elif occasion == "superhero":
        return "Buffet with high-energy and healthy food."
    else:
        return "Custom menu for the butler."

# Tool for catering
@tool
def catering_service_tool(query: str) -> str:
    """
    This tool returns the highest-rated catering service in Gotham City.
    
    Args:
        query: A search term for finding catering services.
    """
    # Example list of catering services and their ratings
    services = {
        "Gotham Catering Co.": 4.9,
        "Wayne Manor Catering": 4.8,
        "Gotham City Events": 4.7,
    }
    
    # Find the highest rated catering service (simulating search query filtering)
    best_service = max(services, key=services.get)
    
    return best_service

# Tool for creative superhero-themed party ideas
@tool
def SuperheroPartyThemeTool(category: str) -> str:
    """
    This tool suggests creative superhero-themed party ideas based on a category.

    Args:
        category: The type of superhero party, for example 'classic heroes',
            'villain masquerade', or 'futuristic Gotham'.
    """
    # Example list of catering services and their ratings
    themes  = {
        "classic heroes": "Justice League Gala: Guests come dressed as their favorite DC heroes with themed cocktails like 'The Kryptonite Punch'.",
        "villain masquerade": "Gotham Rogues' Ball: A mysterious masquerade where guests dress as classic Batman villains.",
        "futuristic Gotham": "Neo-Gotham Night: A cyberpunk-style party inspired by Batman Beyond, with neon decorations and futuristic gadgets."
    }
    
    return themes.get(category.lower(), "Themed party idea not found. Try 'classic heroes', 'villain masquerade', or 'futuristic Gotham'.")

agent = CodeAgent(
    tools=[DuckDuckGoSearchTool(), VisitWebpageTool(), catering_service_tool, SuperheroPartyThemeTool, FinalAnswerTool(), suggest_menu], 
    model=InferenceClientModel(), 
    max_steps=10,
    verbosity_level=2,
    additional_authorized_imports=['datetime']
)

# results = agent.run("Search for the best music recommendations for a party at the Wayne's mansion.")
# print(results)

# # Preparing the menu for the party
# results = agent.run("Prepare a formal menu for the party.")
# print(results)

results = agent.run(
    """
    Alfred needs to prepare for the party. Here are the tasks:
    1. Prepare the drinks - 30 minutes
    2. Decorate the mansion - 60 minutes
    3. Set up the menu - 45 minutes
    4. Prepare the music and playlist - 45 minutes

    If we start right now, at what time will the party be ready?
    """
)
print(results)

# results = agent.run("Give me the best playlist for a party at Wayne's mansion. The party idea is a 'villain masquerade' theme")  
# print(results)
                    