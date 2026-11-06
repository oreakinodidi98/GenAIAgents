import os
import json
import time
import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
import asyncio
from dotenv import load_dotenv
load_dotenv()


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
    runs = 20
    sleep_time_ms = 1000  # Sleep time in milliseconds between requests
    api_runs = []
    # POST https://apim-dev-sc-oa-hol-01.azure-api.net/foundry-dev-sc-oa-hol-01/models/chat/completions?api-version=2024-05-01-preview HTTP/1.1
    #https://apim-dev-sc-oa-hol-01.azure-api.net/foundry-dev-sc-oa-hol-01/models/chat/completions?api-version=2024-05-01-preview
    
    #url = f"{gateway_url}/foundry-dev-sc-oa-hol-01/models/chat/completions?api-version=" + api_version
    url = f"{gateway_url}/foundry-dev-sc-oa-hol-01/models/chat/completions"
    print("Request URL:", url)
    print("API version:", api_version)

    for i in range(runs):
        print(f"Run {i + 1}/{runs}")
        start_time = time.perf_counter()
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

        response_time = time.perf_counter() - start_time

        print("Response time:", response_time, "seconds")
        # Print the response status and response time for each request
        status_text = f"{response.status_code} - {response.reason} | Response time: {response_time:.3f} s"
        # Apply color formatting based on the response status code
        if 200 <= response.status_code < 300:
            status_code_str = f"\x1b[1;32m{status_text}\x1b[0m"
        elif response.status_code >= 400:
            status_code_str = f"\x1b[1;31m{status_text}\x1b[0m"
        else:
            status_code_str = status_text
        # Print the response status with color formatting
        print("Response status:", status_code_str)
        # If the response status code is not 200, print the response text and return
        if response.status_code != 200:
            print(response.text)
            return

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print("The response was not valid JSON:")
            print(response.text)
            return
        # Print the token usage from the response data
        print("Token usage:", data.get("usage"), "\n")

        if "x-ms-region" in response.headers:
            print("x-ms-region:", '\x1b[1;31m'+response.headers.get("x-ms-region")+'\x1b[0m') # this header is useful to determine the region of the backend that served the request
            api_runs.append((response_time, response.headers.get("x-ms-region")))

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

        time.sleep(sleep_time_ms / 1000)  # Add a small delay between requests to avoid overwhelming the server


if __name__ == "__main__":
    main()
