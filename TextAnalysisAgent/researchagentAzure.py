import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI  # Azure-specific import
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI instead of regular OpenAI
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
    azure_deployment="gpt-4o",  # Your deployment name
    temperature=0
)

# Rest of your LangGraph implementation stays the same
class State(TypedDict):
    text: str
    classification: str
    entities: List[str]
    summary: str

def classify_node(state: State):
    """Classify using Azure OpenAI"""
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Classify the following text into one of the categories: News, Blog, Research, or Other.\n\nText: {text}\n\nCategory:"
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