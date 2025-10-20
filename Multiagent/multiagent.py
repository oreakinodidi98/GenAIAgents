import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    AzureAISearchToolDefinition, AzureAISearchToolResource, AISearchIndexResource, ToolResources, AgentThreadCreationOptions
)

load_dotenv() # Load environment variables from .env file

# Pattern 1: Explicit validation with clear error messages
def get_required_env(AZURE_AIPROJECT_ENDPOINT: str) -> str:
    """Get environment variable or raise clear error for GenAI agent setup"""
    value = os.getenv("AZURE_AIPROJECT_ENDPOINT")
    if value is None:
        raise ValueError(f"Missing required environment variable: AZURE_AIPROJECT_ENDPOINT")
    return value

def create_agents_and_tools(project):
    """Create all agents and tools within the project context"""
    # First define the name of search index
    index_name = "ai-search-oahealthplandemo"
    print(f"Using search index: {index_name}")
    # This code retrieves the connection ID for your Azure AI Search resource, then defines and configures the search tool and its resources.
    # Find Azure Cognitive Search connection
    conn_id = None
    for conn in project.connections.list():
        if getattr(conn, "type", None) == "CognitiveSearch":
            conn_id = conn.id
            break
    if not conn_id:
        raise ValueError("No Azure Cognitive Search connection found in this project.")
    
    # Define Azure AI Search tool and resources
    ai_search_tool = AzureAISearchToolDefinition()
    ai_search_resource = AzureAISearchToolResource(
        index_list=[
            AISearchIndexResource(
                index_connection_id=conn_id,
                index_name=index_name
            )
        ]
    )
    tool_resources = ToolResources(azure_ai_search=ai_search_resource)

    # Create agents
    search_agent = project.agents.create_agent(
        model=os.environ["CHAT_MODEL"],
        name="Search-agent",
        instructions="You are a helpful agent that is an expert at searching health documents",
        tools=[ai_search_tool],
        tool_resources=tool_resources
    )
    print(f"Created search agent, ID: {search_agent.id}")
    
    # Report Agent
    report_agent = project.agents.create_agent(
        model="gpt-4o",
        name="report-agent",
        instructions="You are a helpful agent that writes detailed reports about health plans.",
        tools=[],
        tool_resources=None
    )
    print(f"Created report agent, ID: {report_agent.id}")
    
    # Validation Agent
    validation_agent = project.agents.create_agent(
        model="gpt-4o",
        name="validation-agent",
        instructions="""You are a helpful agent that validates health plan reports. 
Check that the report includes ALL of the following:
1. Coverage exclusions (REQUIRED)
2. Deductible information 
3. Premium costs
4. Network provider details
5. Claims process

Return 'Pass' only if ALL criteria are met, otherwise return 'Fail'.
Only return 'Pass' or 'Fail'.""",
        tools=[],
        tool_resources=None
    )
    print(f"Created validation agent, ID: {validation_agent.id}")
    
    return search_agent, report_agent, validation_agent, tool_resources

# Create function called orchestrator to manage the multi-agent workflow
def orchestrator(project, search_agent, report_agent, validation_agent, tool_resources, plan_name: str):
    """Orchestrator function to manage multi-agent workflow"""
    print(f"Orchestrator started for plan: {plan_name}")
    print(f"Using Search Agent ID: {search_agent.id}")
    
    # Step 1: Search Agent - Create thread WITHOUT options parameter
    thread = project.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")
    
    # Add the initial message to the thread
    initial_message = project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Provide detailed information about the {plan_name} health plan."
    )
    
    # Create and process an agent run for search agent
    run = project.agents.runs.create_and_process(
        thread_id=thread.id, 
        agent_id=search_agent.id,
       # tool_resources=tool_resources  # Pass tool resources here instead
    )
    print(f"Search Agent run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
        return {"report_was_generated": False, "content": "Search failed"}

    # Fetch messages from the thread
    messages = project.agents.messages.list(thread_id=thread.id)
    # search_response = ""
    # for msg in messages:
    #     if msg.role == "agent":
    #         search_response = msg.content
    #         print(f"Search Agent Response: {search_response}")
    search_response = extract_last_agent_message(messages)
    print(f"Search Agent Response: {search_response}")

    # Step 2, Report Agent writes the report
    # Pass search response to report agent
    report_thread = project.agents.threads.create()
    
    # Add message to report thread
    project.agents.messages.create(
        thread_id=report_thread.id,
        role="user",
        content=f"Based on the following information, write a detailed report about the health plan:\n{search_response}"
    )
    
    report_run = project.agents.runs.create_and_process(
        thread_id=report_thread.id, 
        agent_id=report_agent.id
    )
    print(f"Report Agent run finished with status: {report_run.status}")


    if report_run.status == "failed":
        print(f"Run failed: {report_run.last_error}")
        return {"report_was_generated": False, "content": "Report generation failed"}

    # Fetch report from the thread
    report_messages = project.agents.messages.list(thread_id=report_thread.id)
    report_content = ""
    for msg in report_messages:
        if msg.role == "agent":
            report_content = msg.content
            print(f"Report Agent Response: {report_content}")
   #report_content = extract_last_agent_message(report_messages)

    # 3. Validation Agent checks the report
    # Pass report to validation agent
    validation_thread = project.agents.threads.create()
    
    # Add message to validation thread
    project.agents.messages.create(
        thread_id=validation_thread.id,
        role="user",
        content=f"Validate that the following report includes coverage exclusions. Here is the report: {report_content}"
    )

    validation_run = project.agents.runs.create_and_process(thread_id=validation_thread.id, agent_id=validation_agent.id)
    print(f"Validation Agent run finished with status: {validation_run.status}")

    if validation_run.status == "failed":
        print(f"Run failed: {validation_run.last_error}")
        return {"report_was_generated": False, "content": "Validation failed"}
    
    # Fetch validation result from the thread
    validation_msgs = project.agents.messages.list(thread_id=validation_run.thread_id)
    validation_result = extract_last_agent_message(validation_msgs)

     # 4. Output result
    if validation_result.strip().lower() == "pass":
        filename = f"{plan_name}_Report.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Report generated and saved to {filename}.")
        return {"report_was_generated": True, "content": report_content}
    else:
        print("Report did not meet validation requirements.")
        return {"report_was_generated": False, "content": "The report could not be generated as it did not meet the required validation standards."}

def extract_last_agent_message(messages):
    """Helper to extract the last agent/assistant message's text"""
    last_msg = None
    for msg in reversed(list(messages)):
        role = getattr(msg, "role", None)
        if role and ("agent" in role.lower() or "assistant" in role.lower()):
            last_msg = msg
            break
    if last_msg and getattr(last_msg, "content", None) and isinstance(last_msg.content, list):
        for part in last_msg.content:
            if part.get("type") == "text" and "text" in part and "value" in part["text"]:
                return part["text"]["value"]
    elif last_msg and isinstance(getattr(last_msg, "content", None), str):
        return last_msg.content
    return ""

def main():
    """Main function that properly manages the client lifecycle"""
    # Initialize client with proper authentication
    project = AIProjectClient(
        endpoint=get_required_env("AZURE_AIPROJECT_ENDPOINT"),
        credential=DefaultAzureCredential()
    )
    
    print("Welcome to the Health Plan Multi-Agent System!")
    
    # Create agents and tools within the project context
    with project:
        search_agent, report_agent, validation_agent, tool_resources = create_agents_and_tools(project)
        
        # Main interaction loop
        while True:
            plan_name = input("Enter the name of a health plan (or 'exit' to quit): ").strip()
            if not plan_name or plan_name.lower() == "exit":
                break
            
            try:
                result = orchestrator(project, search_agent, report_agent, validation_agent, tool_resources, plan_name)
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"Error processing plan '{plan_name}': {e}")
        
        # Cleanup: delete agents
        try:
            project.agents.delete_agent(search_agent.id)
            project.agents.delete_agent(report_agent.id)
            project.agents.delete_agent(validation_agent.id)
            print("Agents deleted successfully.")
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        print("Goodbye!")

if __name__ == "__main__":
    main()