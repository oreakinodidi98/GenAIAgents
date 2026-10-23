import time
import os
import json
import datetime
import requests
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from dotenv import dotenv_values

if os.path.exists(".env"):
    load_dotenv(override=True)
    config = dotenv_values(".env")


apim_resource_gateway_url = os.getenv("APIM_RESOURCE_GATEWAY_URL")
apim_subscription_key = os.getenv("APIM_SUBSCRIPTION_KEY")

openai_api_version = os.getenv("OPENAI_API_VERSION")
openai_model_name = os.getenv("OPENAI_MODEL_NAME")
openai_deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

client = AzureOpenAI(
    azure_endpoint=apim_resource_gateway_url,
    api_key=apim_subscription_key,
    api_version=openai_api_version
)

messages={"messages":[
    {"role": "system", "content": "You are a sarcastic unhelpful assistant."},
    {"role": "user", "content": "Can you tell me the time, please?"}
]}

response = client.chat.completions.create(model=openai_model_name, messages=messages)

print("💬 ", response.choices[0].message.content)