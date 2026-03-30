from langfuse import LangfuseTracer
from langfuse import observe
from langfuse.openai import openai # OpenAI integration
from langchain_openai import ChatOpenAI
import os
from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

# initialise langfuse tracer
