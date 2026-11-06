import time
import os
from dotenv import load_dotenv
import json
import datetime
import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI,OpenAI
import asyncio
load_dotenv()

def required_env(name):
    value = os.getenv(name)
    if not value or not value.strip():
        raise ValueError(f"Missing environment variable: {name}")
    return value.strip()

def main():
    # Test environment variables
    gateway_url = required_env("apim_resource_gateway_url").rstrip("/")
    deployment_name = required_env("openai_deployment_name")
    subscription_key = required_env("apim_subscription_key")
    model_name = required_env("openai_model_name")
    api_version = "2024-05-01-preview"

    print("apim_resource_gateway_url:", gateway_url)
    print("openai_deployment_name:", deployment_name)
    print("apim_subscription_key:", subscription_key)
    print("openai_model_name:", model_name)
    print("api_version:", api_version)
    
    messages=[
        {"role": "system", "content": "You are a sarcastic unhelpful assistant."},
        {"role": "user", "content": "Can you tell me the time, please?"},
    ]

    # # can connect to llm using APIM
    # client = AzureOpenAI(
    #     azure_endpoint=gateway_url,
    #     api_key=subscription_key,
    #     api_version=api_version
    # )
    # response = client.chat.completions.create(
    #         model=model_name, 
    #         messages=messages
    # )

    client = OpenAI(
        base_url=f"{gateway_url}/foundry/models/",
        api_key=subscription_key,
        default_headers={"api-key": subscription_key},
    )

    # invoke service for chat complertion 
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        extra_query={"api-version": api_version},
    )
    
    print("💬 ", response.choices[0].message.content) 

if __name__ == "__main__":
    main()


