import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv  # This was missing!
# Importing necessary Azure libraries for future use
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
#or from langchain_core.prompts import PromptTemplate  # Updated import path
#from langchain_openai import ChatOpenAI
#from langchain_core.messages import HumanMessage   # Updated import path


# Load environment variables
load_dotenv()

# Initialize the ChatOpenAI instance 
llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)
# emperature = 0 in LLMs means the model will always choose the most probable/likely token at each step, making outputs deterministic and consistent. 
# This leads to more focused and precise responses, but potentially less creative ones compared to higher temperature settings which introduce more randomness in token selection.

# Agent memory structure - This is the "brain" of your research agent
class State(TypedDict): 
    """
    State represents what your agent remembers between processing steps.
    Think of this as the agent's working memory.
    """
    text: str              # The input text to analyze
    classification: str    # What type of text this is (article, report, etc.)
    entities: List[str]    # Important people, places, things found
    summary: str          # Key takeaways from the text

# creating agents core capabilities (skills)
# This function determinea what kind of document they're looking at. 
# We use a prompt template to give clear, consistent instructions to our AI model. 
# The function takes in our current state (which includes the text we're analyzing) and returns its classification.
def classify_node(state: State):
    """Classify the type of text into one of the categories: News, Blog, Research, or Other """
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Classify the following text into one of the categories: News, Blog, Research, or Other.\n\nText:{text}\n\nCategory:"
    )
    message = HumanMessage(content=prompt.format(text=state["text"]))
    classification = llm.invoke([message]).content.strip()
    return {"classification": classification}

# Entity extraction function
def extract_entities_node(state: State):
    """Extract important entities from the text"""
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Extract important people, places, and things from the following text.\n\nText:{text}\n\nEntities:"
    )
    message = HumanMessage(content=prompt.format(text=state["text"]))
    entities = llm.invoke([message]).content.strip().split(", ")
    return {"entities": entities}

# Summary generation function
def summarize_node(state: State):
    """Generate a summary of the text"""
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Summarize the following text in a few sentences.\n\nText:{text}\n\nSummary:"
    )
    message = HumanMessage(content=prompt.format(text=state["text"]))
    summary = llm.invoke([message]).content.strip()
    return {"summary": summary}

# Define the state graph for our research agent, connecting these capabilities into a coordinated system

workflow = StateGraph(State)

# Add nodes to the workflow for each capability
workflow.add_node("classify", classify_node)
workflow.add_node("extract_entities", extract_entities_node)
workflow.add_node("summarize", summarize_node)

# add edges to connect the nodes
workflow.set_entry_point("classify") # Set the entry point of the graph
workflow.add_edge("classify", "extract_entities")
workflow.add_edge("extract_entities", "summarize")
workflow.add_edge("summarize", END)

# compile the graph
app = workflow.compile()



# Test your research agent
sample_text = """
OpenAI has announced the GPT-4 model, which is a large multimodal model that exhibits human-level performance on various professional benchmarks. It is developed to improve the alignment and safety of AI systems.
additionally, the model is designed to be more efficient and scalable than its predecessor, GPT-3. The GPT-4 model is expected to be released in the coming months and will be available to the public for research and development purposes.
"""
print("🔍 Research Agent Analysis Starting...")
print("=" * 50)

state_input = {"text": sample_text}
result = app.invoke(state_input)

print("📊 Classification:", result["classification"])
print("\n🏷️ Entities:", result["entities"])
print("\n📝 Summary:", result["summary"])
print("\n" + "=" * 50)
print("✅ Research Agent Analysis Complete!")