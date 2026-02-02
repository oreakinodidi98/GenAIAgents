
from foundry_local import FoundryLocalManager
import openai
import os

alias = "qwen2.5-0.5b"

# Ensure the service starts properly with timeout
manager = FoundryLocalManager(alias)

# dont need a api key because using local model 
client = openai.OpenAI(
    base_url=manager.endpoint, 
    api_key=manager.api_key)

def main():
    print(f"Using model alias: {manager.get_model_info(alias).id}")
    print(f"Using Endpoint: {manager.endpoint}")

    # send request
    request = "Tell me a joke about computers."
    print(f"Sending request to the model {request}")
    response = client.chat.completions.create(
        model=manager.get_model_info(alias).id,
        messages=[
            {"role": "user", "content": request}
        ]
    )
    # print response
    print("Response from model:")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
