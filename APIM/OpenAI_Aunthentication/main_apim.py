import os
import json
import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
import asyncio
from dotenv import load_dotenv
load_dotenv()

# apim_resource_gateway_url = os.getenv("apim_resource_gateway_url")
# openai_deployment_name = os.getenv("openai_deployment_name")
# openai_api_version = os.getenv("openai_api_version")
# apim_subscription_key = os.getenv("apim_subscription_key")

# # create the URL
# url = apim_resource_gateway_url + "/openai/deployments/" + openai_deployment_name + "/chat/completions?api-version=" + openai_api_version

def required_env(name):
    value = os.getenv(name)
    if not value or not value.strip():
        raise ValueError(f"Missing environment variable: {name}")
    return value.strip()

def main():
    gateway_url = required_env("apim_resource_gateway_url").rstrip("/")
    deployment = required_env("openai_deployment_name")
    #api_version = required_env("openai_api_version")
    api_version = "2024-05-01-preview"
    subscription_key = required_env("apim_subscription_key")
    # POST https://apim-dev-sc-oa-hol-01.azure-api.net/foundry/models/chat/completions?api-version=2024-05-01-preview HTTP/1.1
    #https://apim-dev-sc-oa-hol-01.azure-api.net/foundry/models/chat/completions?api-version=2024-05-01-preview
    #url = f"{gateway_url}/foundry/models/chat/completions?api-version=" + api_version
    url = f"{gateway_url}/foundry/models/chat/completions"
    print("Request URL:", url)
    print("API version:", api_version)
    response = requests.post(
        url,
        params={"api-version": api_version},
        headers={"api-key": subscription_key},
        json={
            "model": deployment,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
            "max_completion_tokens": 50,
        },
        timeout=60,
    )

    status_text = f"{response.status_code} - {response.reason}"

    if 200 <= response.status_code < 300:
        status_code_str = f"\x1b[1;32m{status_text}\x1b[0m"
    elif response.status_code >= 400:
        status_code_str = f"\x1b[1;31m{status_text}\x1b[0m"
    else:
        status_code_str = status_text

    print("Response status:", status_code_str)

    if response.status_code != 200:
        print(response.text)
        return

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("The response was not valid JSON:")
        print(response.text)
        return

    print("Token usage:", data.get("usage"), "\n")

    choices = data.get("choices") or []
    if not choices:
        print("No message choices were returned.")
        return

    message = choices[0].get("message") or {}
    content = message.get("content")
    if content:
        print("💬", content, "\n")
    else:
        print("No text content was returned.")
        print("Finish reason:", choices[0].get("finish_reason"))


    # print("Response status:", response.status_code, response.reason)
    # if not response.ok:
    #     print(response.text)
    #     return
    # data = response.json()
    # print("Token usage:", data.get("usage"))
    # print(data["choices"][0]["message"]["content"])


    # # Check the response status code and apply formatting (parsing)
    # if 200 <= response.status_code < 300:
    #     status_code_str = '\x1b[1;32m' + str(response.status_code) + " - " + response.reason + '\x1b[0m'  # Bold and green
    # elif response.status_code >= 400:
    #     status_code_str = '\x1b[1;31m' + str(response.status_code) + " - " + response.reason + '\x1b[0m'  # Bold and red
    # else:
    #     status_code_str = str(response.status_code)  # No formatting
        
    # # Print the response status with the appropriate formatting
    # print("Response status:", status_code_str)

    # if (response.status_code == 200):
    #     data = json.loads(response.text)
    #     print("Token usage:", data.get("usage"), "\n")
    #     print("💬 ", data.get("choices")[0].get("message").get("content"), "\n")
    # else:
    #     print(response.text) 

if __name__ == "__main__":
    main()

