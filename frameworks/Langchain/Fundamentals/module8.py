from langchain_openai import ChatOpenAI
from langchain.agents import create_agent,AgentState
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from random import randint
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import asyncio
# checkpoint
from langchain_azure_cosmosdb import CosmosDBSaverSync
# list all documents in the CosmosDB container to verify that conversation state is being saved
from azure.cosmos import CosmosClient
import json
# summarize message history in an agent, use the built-in SummarizationMiddleware
from langchain.agents.middleware import SummarizationMiddleware,HumanInTheLoopMiddleware

from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

# Middleware to trim message history before sending to the model
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import before_model,after_model
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from typing import Any


from dotenv import load_dotenv
load_dotenv()

# Define custom tools for the agent
@tool
def get_weather(location: str) -> str:
    """Get the current weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    temp = randint(10, 30)
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {temp}°C."
# Define another custom tool for the agent
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together.

    Args:
        a: first number
        b: second number
    """
    return a * b
@tool
def write_file(path: str, content: str) -> str:
    """Write `content` to the file at `path`. Sensitive: requires approval."""
    # In a real app this would touch the filesystem.
    return f"Wrote {len(content)} chars to {path}"


@tool
def execute_sql(query: str) -> str:
    """Execute a SQL statement. Sensitive: requires approval (no edits)."""
    # In a real app this would run against a database.
    return f"Executed: {query}"


@tool
def read_data(table: str) -> str:
    """Read rows from a table. Safe: no approval needed."""
    return f"Read 3 rows from {table}"

# Middleware to trim message history before sending to the model
@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the last few messages to fit context window."""
    messages = state["messages"]

    if len(messages) <= 3:
        return None  # No changes needed

    first_msg = messages[0]
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    new_messages = [first_msg] + recent_messages

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages
        ]
    }

@after_model
def validate_response(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove messages containing sensitive words."""
    STOP_WORDS = ["password", "secret"]
    last_message = state["messages"][-1]

    if any(word in last_message.content for word in STOP_WORDS):
        return {"messages": [RemoveMessage(id=last_message.id)]}
    
    return None

async def main():
    # Test environment variables
    print("endpoint:", os.getenv("FOUNDRY_ENDPOINT"))
    print("deployment:", os.getenv("LLM_MODEL_DEPLOYMENT_NAME"))
    print("CosmosDB Endpoint:", os.getenv("COSMOSDB_ENDPOINT"))
    print("CosmosDB Key:", os.getenv("COSMOSDB_KEY"))
    

    # define tools for the agent
    tools = [get_weather, multiply, execute_sql, write_file, read_data]
    print("Registered tools:", [t.name for t in tools])

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
    response = model.stream([HumanMessage(content="Tell me about Nigeria.")])
    # print response chunks as they arrive
    for chunk in response:
        print(chunk.content, end="", flush=True)
    
    # initialise CosmosDB saver
    # print(f"\ninitialising CosmosDB checkpointer...")
    # checkpointer = CosmosDBSaverSync(
    #     database_name="langgraph-memory",
    #     container_name="checkpoints",
    #     endpoint=os.getenv("COSMOSDB_ENDPOINT"),
    #     key=os.getenv("COSMOSDB_KEY"),
    # )
    # print(f"\nCosmosDB checkpointer initialised.")


    # use this for POC, as it stores memory in-memory rather than in CosmosDB
    print(f"\ninitialising in-memory checkpointer...")
    memory_saver = InMemorySaver()
    print(f"\nIn-memory checkpointer initialised.")

    # Use a unique thread_id — all messages with the same thread_id share memory
    print(f"\nusing thread_id: demo-thread-1")
    config = {"configurable": {"thread_id": "thread-1"}}
    
    print(f"\ncreating agent...")
    # create agent with the llm model, tools, middleware, and checkpointer
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="You are a helpful Solutions architect running a demo with Langchain and CosmosDB.",
        middleware=[SummarizationMiddleware(
            # can use different model for summerisation if wanted
            model=model,
            trigger=("tokens", 4000),
            keep=("messages", 20)
        ), HumanInTheLoopMiddleware(
            interrupt_on={
                # All decisions allowed: approve, edit, reject, respond
                "write_file": True,
                # Only approve or reject (no editing of the SQL query)
                "execute_sql": {"allowed_decisions": ["approve", "reject"]},
                # Safe read-only operation: no need to approve so specify false
                "read_data": False,
                "multiply": False,
                "get_weather": False
            },
            description_prefix="Tool execution pending approval",
        ),
        trim_messages,
        validate_response,
        ],
        checkpointer=memory_saver,
    )

    print(f"\ngetting response from agent in streaming mode...")
    agent.invoke({"messages": "hi, my name is bob"}, config)
    agent.invoke({"messages": "write a short poem about cats"}, config)
    agent.invoke({"messages": "now do the same but for dogs"}, config)

    # ask agent about my name
    response = agent.invoke({"messages": "what's my name?"}, config)
    for msg in response["messages"]:
        msg.pretty_print()
    # ask agent to write a password in the response
    response = agent.ainvoke({"messages": "write a password in the response"}, config)
    for msg in response["messages"]:
        msg.pretty_print()
    
    # ask agent to multiply two numbers
    async for step in agent.astream(
        {"messages": [HumanMessage(content="Multiply 6 by 7")]},
        config=config,
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

    # ask agent about the weather
    async for step in agent.astream(
        {"messages": [HumanMessage(content="I live in UK. What's the weather like in Amsterdam?")]},
        config=config,
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

    # ask agent about my name
    async for step in agent.astream(
        {"messages": [HumanMessage(content="What's my name and where do i live?")]},
        config=config,
        stream_mode="values"
    ):
        step["messages"][-1].pretty_print()
    # ask agent about my name
    result = agent.invoke(
        {"messages": [HumanMessage(content="Please run this SQL to clean up old data: "
                                            "DELETE FROM records WHERE created_at < NOW() - INTERVAL '30 days';")]},
        config=config,
        version="v2",
    )
    # The agent paused -- inspect the actions awaiting review.
    print(result.interrupts)
    # approve the pending action
    approved = agent.invoke(
        # pass the approved action to resume the agent
        Command(resume={"decisions": [{"type": "approve"}]}),
        config=config,
        version="v2",
    )

    for msg in approved.value["messages"]:
        msg.pretty_print()
    # Create new thread
    print(f"\nusing thread_id: thread-2")
    new_config = {"configurable": {"thread_id": "thread-2"}}
    result = agent.invoke(
            {"messages": [HumanMessage(content="Write the text 'hello world' to the file /tmp/note.txt")]},
            config=new_config,
            version="v2",
    )
    # Show what the model proposed before we override it.
    print(result.interrupts)

    # Resume with an edited action: change the path and content.
    edited = agent.invoke(
        Command(
            resume={
                "decisions": [
                    {
                        "type": "edit",
                        "edited_action": {
                            "name": "write_file",
                            "args": {
                                "path": "/tmp/note-edited.txt",
                                "content": "hello world (reviewed by human)",
                            },
                        },
                    }
                ]
            }
        ),
        config=new_config,
        version="v2",
    )

    for msg in edited.value["messages"]:
        msg.pretty_print()

    print(f"\nlisting all documents in CosmosDB container...")
    client = CosmosClient(os.getenv("COSMOSDB_ENDPOINT"), os.getenv("COSMOSDB_KEY"))
    database = client.get_database_client("langgraph-memory")
    container = database.get_container_client("checkpoints")
    for item in container.read_all_items():
        print(json.dumps(item, indent=2))

if __name__ == "__main__":
    asyncio.run(main())