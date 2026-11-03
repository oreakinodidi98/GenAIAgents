import asyncio
import random
import sys
from copilot import CopilotClient
from copilot.session import PermissionHandler
from copilot.tools import define_tool
from copilot.session_events import SessionEvent, SessionEventType
from pydantic import BaseModel, Field

RESPONSE_TIMEOUT_SECONDS = 180.0


class GetWeatherParams(BaseModel):
    city: str = Field(description="The name of the city to get weather for")

@define_tool(description="Get simulated weather for a city (random demo data, not live weather)")
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


async def main() -> None:
    client = CopilotClient()
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
        tools=[get_weather],
    )
    session.on(handle_event)

    print("🌤️  Weather Assistant (type 'exit' to quit)")
    print("   Demo uses random weather data, not a live weather service.")
    print("   Try: 'What's the weather in Paris?' or 'Compare weather in NYC and LA'\n")

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