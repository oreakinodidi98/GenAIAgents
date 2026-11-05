import time
import os
from dotenv import load_dotenv
import json
import datetime
import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
import asyncio
load_dotenv()

apim_resource_gateway_url = os.getenv("apim_resource_gateway_url")
openai_deployment_name = os.getenv("openai_deployment_name")
openai_api_version = os.getenv("openai_api_version")
apim_subscription_key = os.getenv("apim_subscription_key")
openai_model_name = os.getenv("openai_model_name")


def main():
    # Test environment variables
    print("apim_resource_gateway_url:", os.getenv("apim_resource_gateway_url"))
    print("openai_deployment_name:", os.getenv("openai_deployment_name"))
    print("apim_subscription_key:", os.getenv("apim_subscription_key"))
    # 
    messages={"messages":[
        {"role": "system", "content": "You are a sarcastic unhelpful assistant."},
        {"role": "user", "content": "Can you tell me the time, please?"}
    ]}
    # can connect to llm using APIM
    client = AzureOpenAI(
        azure_endpoint=apim_resource_gateway_url,
        api_key=apim_subscription_key,
        api_version=openai_api_version
    )
    # invoke service for chat complertion 
    response = client.chat.completions.create(model=openai_model_name, messages=messages)

    print("💬 ", response.choices[0].message.content) 

if __name__ == "__main__":
    asyncio.run(main())