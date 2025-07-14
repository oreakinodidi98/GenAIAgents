import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

def test_agent_setup():
    """Test basic GenAI agent setup - a crucial first step in agent development"""
    
    # Load environment variables - essential for secure API key management
    load_dotenv()
    
    # Verify API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Initialize the ChatOpenAI instance with explicit configuration
    # gpt-4o-mini is cost-effective for learning and testing
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,  # Controls creativity vs consistency
        api_key=api_key   # Explicit API key passing (optional but clear)
    )
    
    # Test the setup with a simple prompt
    try:
        response = llm.invoke("Hello! Are you working? Please respond with your model name.")
        print(f"✅ Agent setup successful!")
        print(f"Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ Agent setup failed: {e}")
        return False

if __name__ == "__main__":
    test_agent_setup()