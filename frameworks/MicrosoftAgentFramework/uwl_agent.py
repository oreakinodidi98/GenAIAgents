from dotenv import load_dotenv
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from search_index_manager import SearchIndexManager
from openai import AsyncAzureOpenAI
from pydantic import Field, BaseModel
from typing import Annotated
from agent_framework.azure import AzureOpenAIResponsesClient, AzureOpenAIChatClient
from agent_framework import (
    AgentExecutor, 
    AgentRunUpdateEvent, 
    WorkflowBuilder, 
    WorkflowOutputEvent,
    WorkflowStatusEvent, 
    WorkflowViz, 
    AgentExecutorResponse)

class QueryIntent(BaseModel):
    """Structured output model for request information."""
    query: str = Field(description="The query string for information retrieval")
    intent: str = Field(description="The intent behind the query")
    topics: list[str] = Field(description="List of topics related to the query")

class RAGAnswer(BaseModel):
    answer: str = Field(description="Final answer to the student.")
    used_sources: list[str] = Field(default=[], description="Search results used.")

load_dotenv() # Load environment variables from .env file
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_AI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_AI_CHAT_DEPLOYMENT_NAME")
# RAG Search variables
SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
#SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
SEARCH_INDEX_NAME = 'ai-search-uwl'
AZURE_SEARCH_MODEL = os.getenv("AZURE_SEARCH_MODEL")
# Define embedding dimensions
embed_dimensions = 1536
azure_search_credential = AzureKeyCredential(SEARCH_API_KEY)
# Create embeddings client that we can reference later
embeddings_client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-01"
)
# Create Search Index Manager
search_index_manager = SearchIndexManager(
    endpoint=SEARCH_ENDPOINT,
    credentials=azure_search_credential,
    model=AZURE_SEARCH_MODEL,
    api_key=SEARCH_API_KEY,
    index_name=SEARCH_INDEX_NAME,
    dimension=embed_dimensions,  # Use the defined variable
    embeddings_client=embeddings_client  # Use the defined variable
)

# define a dumy function (tool) to raise support tickets
def raise_ticket(
    category: Annotated[str, Field(description="Type of issue the student has")]
) -> str:
    """Raise a support ticket for a given issue."""
    # Simulate an API call to raise a support ticket
    print(f"�️ Raising support ticket for issue: {category}...")
    return "Ticket #12345 created successfully."

# define a fake function to check application status
async def check_application_status(
    student_id: Annotated[str, Field(description="The student’s university application ID")]
) -> str:
    return f"Application status for {student_id}: Submitted and under review."

async def book_appointment(
    service: Annotated[str, Field(description="Type of service to book, example: finance, academic support, wellbeing")]
) -> str:
    return f"An appointment has been booked with the {service} team. You will receive an email confirmation shortly."

async def reset_password(
    email: Annotated[str, Field(description="Student email that needs a password reset")]
) -> str:
    return f"A password reset link has been sent to {email}."

async def get_timetable(
    student_id: Annotated[str, Field(description="Student ID")]
) -> str:
    return f"Timetable for {student_id}: Monday 10am Lecture, Wednesday 1pm Lab, Friday 9am Seminar."

async def submit_document(
    document_type: Annotated[str, Field(description="Type of document being submitted")]
) -> str:
    return f"Your {document_type} has been submitted successfully."

async def search_by_topic(
    topic: Annotated[str, Field(description="Topic such as finance, accommodation, IT, library")]
) -> str:
    context = await search_index_manager.search(topic)
    return context or "No information found on that topic."

# define a tool that will go to the for search_university_knowledge
async def search_university_knowledge(
    query: Annotated[str, Field(description="Get information from the RAG about the university.")],
) -> str:
    """Get information from the RAG."""
    try:
        context = await search_index_manager.search(query)
        if context:
            print("📚 Retrieved context from RAG:")
            return context
        else:
            return "No information found."
    except Exception as e:
        print(f"❌ Error details: {type(e).__name__}: {str(e)}")  # DEBUG
        import traceback
        traceback.print_exc()  # Print full traceback
        return f"Error fetching information from RAG: {str(e)}"

# conditional function to determine routing decisions
def route_by_intent(message: AgentExecutorResponse, target_intent: str) -> bool:
    """Return True if classifier agent predicted a given intent."""
    try:
        classification = QueryIntent.model_validate_json(message.agent_run_response.text)
        return classification.intent == target_intent
    except:
        return False


async def main() -> None:
   # create a chat client with azure openai response and a toolset
    chat_client = AzureOpenAIChatClient(
            endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY,
            deployment_name=AZURE_OPENAI_DEPLOYMENT
    )
    try:
        #initialise search index manager
        await search_index_manager.ensure_index_created(
            vector_index_dimensions=embed_dimensions if embed_dimensions else 100
        )

        # create first agent for workflow
        classifier_agent = AgentExecutor(
            chat_client.create_agent(
                model=AZURE_OPENAI_DEPLOYMENT,
                name="UWL-classifier-agent",
                instructions=(
                    "You classify student queries so they can be routed to the correct handler. "
                    "Read the user’s message and identify the intent and topic. "
                    "Return a structured object with one intent value: 'faq', 'process', or 'unknown'. "
                    "If relevant, include a topic such as admissions, finance, accommodation, library, or IT. "
                    "Do not answer the question yourself. Only classify it."
                ),
                tools=[],
                response_format=QueryIntent    
                )
        )
        # create second agent for workflow
        workflow_agent = AgentExecutor(
            chat_client.create_agent(
                model=AZURE_OPENAI_DEPLOYMENT,
                name="UWL-workflow-agent",
                instructions=(
                    "You support UWL student requests that require an action or workflow step rather than an informational answer. "
                    "If the user query requires a process to be triggered, call the appropriate tool. "
                    "If no matching action exists, respond with a helpful message explaining that the request cannot be completed. "
                    "Keep responses short, clear, and accurate."
                ),
                tools=[raise_ticket, check_application_status, book_appointment, reset_password, get_timetable, submit_document],
                )
        )
        #create third agent for workflow with conditional RAG tool usage
        RAG_agent = AgentExecutor(
            chat_client.create_agent(
                model=AZURE_OPENAI_DEPLOYMENT,
                name="RAG-agent",
                instructions=(
                    "You answer student questions using the university’s approved knowledge base. "
                    "Your input is a structured object containing the detected intent and topic. "
                    "Use this context to provide a clear and helpful answer drawn only from the RAG knowledge source. "
                    "If the RAG provides no relevant information, reply with a polite fallback message. "
                    "Keep responses accurate, student-friendly, and easy to read."
                ),
                tools=[search_university_knowledge, search_by_topic],
                response_format=RAGAnswer    
            )
        )
        
        # create workflow by chaining agents using edge
        workflow= (
            WorkflowBuilder()
            .set_start_executor(classifier_agent)
            .add_edge(classifier_agent, workflow_agent, condition=lambda m: route_by_intent(m, "process"))
            .add_edge(classifier_agent, RAG_agent, condition=lambda m: route_by_intent(m, "faq"))
            .build()
        )

        print(f"Created workflow")
        #visualise workflow
        viz= WorkflowViz(workflow)
        doc_diagram = viz.save_svg("docs/uwl_agents_in_workflow_diagram.svg")
        print("Saved workflow diagram as 'uwl_agents_in_workflow_diagram.svg'")
        # run workflow
        events = workflow.run_stream(
            "How do I apply for accommodation? and how do i change courseswhat were the latest finacial reports for the uni and the student code of conduct"
        )

        last_executor_id: str | None = None

        async for event in events:
            if isinstance(event, AgentRunUpdateEvent):
                #print(f"\n🔄 Workflow Status Update: {event}")
                # handle streamming updates from agents
                if event.executor_id != last_executor_id:
                    if last_executor_id is not None:
                        print("\n--- Switching to next agent ---\n")
                    print(f"🤖 Agent ({event.executor_id}) Response Update:")
                    last_executor_id = event.executor_id
                print(event.data, end='', flush=True)
            elif isinstance(event, WorkflowStatusEvent):
                print("\n🔔 Workflow Status Event:")
                print(event)
            
    finally:
        # close search index manager conections
        await search_index_manager.close()
        await embeddings_client.close()
        pass

if __name__ == "__main__":
    asyncio.run(main())
