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

url = f"{apim_resource_gateway_url}/foundry/models/chat/completions"

messages={"messages":[
    {"role": "system", "content": "You are a sarcastic unhelpful assistant."},
    {"role": "user", "content": "Can you tell me the time, please?"}
]}

response = requests.post(url, headers = {'api-key':apim_subscription_key}, json = messages)

# Check the response status code and apply formatting
if 200 <= response.status_code < 300:
    status_code_str = '\x1b[1;32m' + str(response.status_code) + " - " + response.reason + '\x1b[0m'  # Bold and green
elif response.status_code >= 400:
    status_code_str = '\x1b[1;31m' + str(response.status_code) + " - " + response.reason + '\x1b[0m'  # Bold and red
else:
    status_code_str = str(response.status_code)  # No formatting
    
# Print the response status with the appropriate formatting
print("Response status:", status_code_str)

if (response.status_code == 200):
    data = json.loads(response.text)
    print("Token usage:", data.get("usage"), "\n")
    print("💬 ", data.get("choices")[0].get("message").get("content"), "\n")
else:
    print(response.text) 