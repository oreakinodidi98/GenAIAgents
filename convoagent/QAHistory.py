from langchain_openai import AzureChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
    azure_deployment="gpt-4o",  # your Azure deployment name
    temperature=0
)

# Memory store for chat history
store = {}
def get_chat_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Your task is to answer the user's question clearly."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])

# Create the LLMChain
# prompt | llm means: take the prompt, send it to the LLM, and get a response.
qa_chain = prompt | llm

# wrap the chain with history
qa_chain_with_history = RunnableWithMessageHistory(
    # wraps qa_chain with memory, so it remembers what was said before:
    qa_chain,
    # This function retrieves the chat history for the given session ID.
    get_chat_history,
    # this tells the model where to find the new user question.
    input_messages_key="question",
    # This tells the model where the memory (chat history) should be inserted.
    history_messages_key="history"
    
)

# get answer function, includes session_id and uses history chain
def get_answer_with_history(question: str, session_id: str):
    # the function akes a question and a session_id, Passes them to your memory-aware chain.
    return qa_chain_with_history.invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}}
    ).content
# Returns just the AI's reply as a string.

# Example usage
session_id = "user_123"

while True:
    user_question = input("Enter your question (or 'exit' to quit): ")
    if user_question.lower() == "exit":
        break
    answer = get_answer_with_history(user_question, session_id)
    print("AI:", answer)

# print full history at the end
print("\nConversation History:")
for message in store[session_id].messages:
    print(f"{message.type.capitalize()}: {message.content}")
