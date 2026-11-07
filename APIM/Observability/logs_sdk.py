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

runs = 9
sleep_time_ms = 0

def required_env(name):
    value = os.getenv(name)
    if not value or not value.strip():
        raise ValueError(f"Missing environment variable: {name}")
    return value.strip()

def main():

    for i in range(runs):
        print("▶️ Run: ", i+1)
        # Test environment variables
        gateway_url = required_env("apim_resource_gateway_url").rstrip("/")
        deployment_name = required_env("openai_deployment_name")
        subscription_key = required_env("apim_subscription_key")
        model_name = required_env("openai_model_name")
        api_version = "2024-05-01-preview"
        backend_url = required_env("apim_backend_url")

        print("apim_resource_gateway_url:", gateway_url)
        print("openai_deployment_name:", deployment_name)
        print("apim_subscription_key:", subscription_key)
        print("openai_model_name:", model_name)
        print("api_version:", api_version)
        print("apim_backend_url:", backend_url)
        
        messages=[
            {"role": "system", "content": "You are a sarcastic unhelpful assistant with a mean streak."},
            {"role": "user", "content": "Can you tell me the time, please and the purpose of life?"},
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
            base_url=f"{gateway_url}/{backend_url}/models",
            api_key=subscription_key,
            default_headers={"api-key": subscription_key,
                             "Ocp-Apim-Subscription-Key": subscription_key,
            },
        )

        start_time = time.perf_counter()
        # invoke service for chat complertion 
        response = client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            extra_query={"api-version": api_version},
        )
        
        response_time = time.perf_counter() - start_time
        print("💬 ", response.choices[0].message.content) 
        print("Response time:", response_time, "seconds")
        time.sleep(sleep_time_ms / 1000)  # Add a small delay between requests to avoid overwhelming the server

        # change to sub key 2
        client = OpenAI(
            base_url=f"{gateway_url}/{backend_url}/models",
            api_key=subscription_key,
            default_headers={"api-key": subscription_key,
                            "Ocp-Apim-Subscription-Key": subscription_key,
            },
        )
        response = client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            extra_query={"api-version": api_version},
        )
        print("💬 ","for subscription 2: ", response.choices[0].message.content)
        response_time = time.perf_counter() - start_time
        print("Response time for subscription 2:", response_time, "seconds")
        

if __name__ == "__main__":
    main()


