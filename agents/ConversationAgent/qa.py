from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
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

# memory store for chat history
store = {}
def get_chat_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# prompt template
template = """
You are a helpful AI assistant. Your task is to answer the user's question to the best of your ability.

User's question: {question}

Please provide a clear and concise answer:
"""

prompt = PromptTemplate(template=template, input_variables=["question"])

# Create the LLMChain
qa_chain  = prompt | llm

# create get answer function

def get_answer(question):
    """
    Get an answer to the given question using the QA chain.
    """
    input_variables = {"question": question}
    response = qa_chain.invoke(input_variables).content
    return response

# wrap the chain with history
chain_with_history = RunnableWithMessageHistory(
    qa_chain,
    get_chat_history,
    input_messages_key="question",
    history_messages_key="history"
)

# Example usage

session_id = "user_123"
user_question = input("Enter your question: ")
user_answer = get_answer(user_question)
print(f"Answer: {user_answer}")