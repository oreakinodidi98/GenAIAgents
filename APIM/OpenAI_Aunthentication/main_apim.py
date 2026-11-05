import time
import os
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

# create the URL
url = apim_resource_gateway_url + "/openai/deployments/" + openai_deployment_name + "/chat/completions?api-version=" + openai_api_version

def main():
    # Test environment variables
    print("apim_resource_gateway_url:", os.getenv("apim_resource_gateway_url"))
    print("openai_deployment_name:", os.getenv("openai_deployment_name"))
    print("apim_subscription_key:", os.getenv("apim_subscription_key"))
    # Send request
    messages={"messages":[
        {"role": "system", "content": "You are a sarcastic unhelpful assistant."},
        {"role": "user", "content": "Can you tell me the time, please?"}
    ]}
    # get responce, Adding API key to authenticate
    response = requests.post(url, headers = {'api-key':apim_subscription_key}, json = messages)

    # Check the response status code and apply formatting (parsing)
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

if __name__ == "__main__":
    asyncio.run(main())