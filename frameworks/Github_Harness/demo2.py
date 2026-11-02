import asyncio
import sys
from copilot import CopilotClient
from copilot.session import PermissionHandler
from copilot.session_events import SessionEventType

async def main():
    # set client as copilot
    client = CopilotClient()
    # initilise client
    await client.start()
    # start a session
    session = await client.create_session(on_permission_request=PermissionHandler.approve_all, model="auto", streaming=True)

    # Listen for response chunks
    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()
        if event.type == SessionEventType.SESSION_IDLE:
            print()  # New line when done
    # handle session events
    session.on(handle_event)
    # send a message and wait for the response
    await session.send_and_wait("Tell me a short joke")
    # stop the client
    await client.stop()

asyncio.run(main())