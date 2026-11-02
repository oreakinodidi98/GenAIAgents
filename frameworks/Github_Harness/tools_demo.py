import asyncio
import random
import sys
from copilot import CopilotClient
from copilot.session import PermissionHandler
from copilot.tools import define_tool
from copilot.session_events import SessionEventType
from pydantic import BaseModel, Field

# Define the parameters for the tool using Pydantic
class GetWeatherParams(BaseModel):
    city: str = Field(description="The name of the city to get weather for")

# Define a tool that Copilot can call
@define_tool(description="Get the current weather for a city")
async def get_weather(params: GetWeatherParams) -> dict:
    city = params.city
    # In a real app, you'd call a weather API here
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
    temp = random.randint(50, 80)
    condition = random.choice(conditions)
    return {"city": city, "temperature": f"{temp}°F", "condition": condition}

async def main():
    # Initialize the Copilot client
    client = CopilotClient()
    # Start the Copilot client
    await client.start()
    # Start a session is like creating an agent
    session = await client.create_session(on_permission_request=PermissionHandler.approve_all, model="auto", streaming=True, tools=[get_weather])

    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()
        if event.type == SessionEventType.SESSION_IDLE:
            print()
    # Register the event handler with the session
    session.on(handle_event)
    # Send a message to the session and wait for the response
    await session.send_and_wait("What's the weather like in Seattle and Tokyo?")

    await client.stop()

asyncio.run(main())