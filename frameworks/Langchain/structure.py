import os
from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

# Define the structured output schema using Pydantic (Python's equivalent to Zod)
class UserMessage(BaseModel):
    """Schema for extracting contact information - the 'structure' your agent will follow"""
    name: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email address of the user")
    company: Optional[str] = Field(default=None, description="The company of the user")

# Initialize Azure OpenAI client
llm = AzureChatOpenAI(
  model="gpt-4o",
  temperature=0,
  max_tokens=None,
  max_retries=2,
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
  azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_version="2024-12-01-preview"  # Specify API version for Azure
);

# Create the structured output model
model_with_structure = llm.with_structured_output(UserMessage)

# Test the extraction
def extract_contact_info():
    """Test function to demonstrate structured extraction"""
    prompt = """
    Extract name, email and company from this message:
    ---
    Hi, I'm Ore from Microsoft. You can reach me at ore@notmyemail.com.
    ---
    """
    
    try:
        result = model_with_structure.invoke(prompt)
        print(f"✅ Extraction successful!")
        print(f"Name: {result.name}")
        print(f"Email: {result.email}")
        print(f"Company: {result.company}")
        return result
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return None

if __name__ == "__main__":
    extract_contact_info()