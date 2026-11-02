import asyncio
import random
import sys
from copilot import CopilotClient
from copilot.session import PermissionHandler
from copilot.tools import define_tool
from copilot.session_events import SessionEventType
from pydantic import BaseModel, Field

class GetWeatherParams(BaseModel):
    city: str = Field(description="The name of the city to get weather for")

@define_tool(description="Get the current weather for a city")
async def get_weather(params: GetWeatherParams) -> dict:
    city = params.city
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
    temp = random.randint(50, 80)
    condition = random.choice(conditions)
    return {"city": city, "temperature": f"{temp}°F", "condition": condition}

async def main():
    client = CopilotClient()
    await client.start()

    sandboxConfig = {
        "enabled": True,
        "sandboxMcpServers": True,
        "userPolicy": { "network": { "allowOutbound": False } },
    }

    session = await client.create_session(
        on_permission_request=PermissionHandler.approve_all, 
        model="auto", 
        streaming=True, 
        tools=[get_weather],
        sandboxConfig=sandboxConfig,
        # Remote MCP server (HTTP)
        mcpServers={
            "github": {
                "type": "http",
                "url": "https://api.githubcopilot.com/mcp/",
            },
        }
    )

    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()

    session.on(handle_event)

    print("🌤️  Weather Assistant (type 'exit' to quit)")
    print("   Try: 'What's the weather in Paris?' or 'Compare weather in NYC and LA'\n")

    while True:
        try:
            user_input = input("You: ")
        except EOFError:
            break

        if user_input.lower() == "exit":
            break

        sys.stdout.write("Assistant: ")
        await session.send_and_wait(user_input)
        print("\n")

    await client.stop()

asyncio.run(main())