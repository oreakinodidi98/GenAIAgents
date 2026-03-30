from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI  
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
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Create the LLMChain
chain = prompt | llm

# wrap the chain with history
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_chat_history,
    input_messages_key="input",
    history_messages_key="history"
)

# Example usage
session_id = "user_123"


response1 = chain_with_history.invoke(
    {"input": "Hello! How are you?"},
    config={"configurable": {"session_id": session_id}}
)
print("AI:", response1.content)

response2 = chain_with_history.invoke(
    {"input": "What was my previous message?"},
    config={"configurable": {"session_id": session_id}}
)
print("AI:", response2.content)

# print the response
print("\nConversation History:")
for message in store[session_id].messages:
    print(f"{message.type}: {message.content}")