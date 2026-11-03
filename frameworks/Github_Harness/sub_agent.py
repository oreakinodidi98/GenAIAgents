import asyncio
import random
import sys
from copilot import CopilotClient, CopilotClientOptions
from copilot.session import PermissionHandler
from copilot.tools import define_tool
from copilot.session_events import SessionEventType, SessionEvent
from pydantic import BaseModel, Field

RESPONSE_TIMEOUT_SECONDS = 180.0

class GetWeatherParams(BaseModel):
    city: str = Field(description="The name of the city to get weather for")

@define_tool(description="Get the current weather for a city")
async def get_weather(params: GetWeatherParams) -> dict:
    city = params.city
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
    temp = random.randint(50, 80)
    condition = random.choice(conditions)
    return {"city": city, "temperature": f"{temp}°F", "condition": condition}


def handle_event(event: SessionEvent) -> None:
    """Display streamed text and runtime diagnostics instead of hiding failures."""
    if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
        sys.stdout.write(event.data.delta_content or "")
        sys.stdout.flush()
    elif event.type == SessionEventType.SESSION_ERROR:
        print(f"\nCopilot error: {event.data.message}", file=sys.stderr, flush=True)
    elif event.type == SessionEventType.TOOL_EXECUTION_START:
        print(f"\n[Calling tool: {event.data.tool_name}]", flush=True)
    elif event.type == SessionEventType.TOOL_EXECUTION_COMPLETE and not event.data.success:
        print(f"\nTool failed: {event.data.error}", file=sys.stderr, flush=True)

async def main():
    client = CopilotClient(
        # Configure the Copilot client with options to enable telemetry
        CopilotClientOptions(
            telemetry={
                "otlp_endpoint": "http://localhost:4318",
            },
        )
    )
    await client.start()

    """Run the demo with authentication checks and bounded response waits."""
    auth = await client.get_auth_status()
    if not auth.isAuthenticated:
        print(
                "Copilot is not authenticated. Run 'copilot' in this terminal, "
                "use '/login', then rerun this script.",
                file=sys.stderr,
            )
        return

    session = await client.create_session(
        on_permission_request=PermissionHandler.approve_all,
        model="auto",
        streaming=True,
        system_message={
            "content": "You are a helpful assistant for our engineering team. Always be concise. The researcher and editor agent respond to you",
        },
        tools=[get_weather],
        skillDirectories=["../.github/skills"],
        custom_agents=[
        {
            "name": "researcher",
            "display_name": "Research Agent",
            "description": "Explores codebases and answers questions using read-only tools",
            "tools": ["grep", "glob", "view"],
            "prompt": "You are a research assistant. Analyze code and answer questions. Do not modify any files.",
        },
        {
            "name": "dangerous-cleanup",
            "display_name": "Cleanup Agent"
            "description": "Deletes unused files and dead code",
            "tools": ["bash", "edit", "view"],
            "prompt": "You clean up codebases by removing dead code and unused files.",
            "infer": false, // Only invoked when user explicitly asks for this agent
        },
        {
            "name": "editor",
            "display_name": "Editor Agent",
            "description": "Makes targeted code changes",
            "tools": ["view", "edit", "bash"],
            "prompt": "You are a code editor. Make minimal, surgical changes to files as requested.",
        },
        ],
        # Remote MCP server (HTTP)
        mcp_servers={
            "github": {
                "type": "http",
                "url": "https://api.githubcopilot.com/mcp/",
            },
        },
    )

    session.on(handle_event)

    print("  Research Assistant (type 'exit' to quit)")
    print("   Try: 'What's the code base about?' or 'Compare the meaning of these 2 different code'\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break

        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        print("Assistant: ", end="", flush=True)
        try:
            await session.send_and_wait(user_input, timeout=RESPONSE_TIMEOUT_SECONDS)
        except TimeoutError:
            print(
                        f"\nCopilot did not finish within {RESPONSE_TIMEOUT_SECONDS:g} seconds. "
                        "Cancelling this request. Check the errors above, your network, "
                        "and Copilot model access before retrying.",
                        file=sys.stderr,
                        flush=True,
                )
            # The SDK timeout stops waiting but does not stop agent work.
            await session.abort()
        print("\n")

if __name__ == "__main__":
    asyncio.run(main())