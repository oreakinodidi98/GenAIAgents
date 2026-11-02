import asyncio
import random
import sys
from copilot import CopilotClient, PermissionDecisionApproveOnce
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

    session = await client.create_session(
        on_permission_request=PermissionHandler.approve_all,
        inv: PermissionDecisionApproveOnce(),
        model="auto", 
        streaming=True, 
        tools=[get_weather],
        custom_agents=[
        {
            "name": "researcher",
            "display_name": "Research Agent",
            "description": "Explores codebases and answers questions using read-only tools",
            "tools": ["grep", "glob", "view"],
            "prompt": "You are a research assistant. Analyze code and answer questions. Do not modify any files.",
        },
        {
            "name": "editor",
            "display_name": "Editor Agent",
            "description": "Makes targeted code changes",
            "tools": ["view", "edit", "bash"],
            "prompt": "You are a code editor. Make minimal, surgical changes to files as requested.",
        },],
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

    print("  Research and editor Assistant (type 'exit' to quit)")
    print("   Try: 'What's the code base about?' or 'Compare the meaning of these 2 different code'\n")

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