import time
import os
import json
import datetime
import requests
import asyncio
from openai import AsyncOpenAI, AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from dotenv import dotenv_values

# Load environment variables from .env file if it exists
if os.path.exists(".env"):
    load_dotenv(override=True)
    config = dotenv_values(".env")

# Get the LLM endpoint from environment variables
llm_endpoint = os.getenv("LLM_ENDPOINT")
llm_model = os.getenv("LLM_MODEL")

# Initialize the AsyncOpenAI client with the LLM endpoint
client = AsyncOpenAI(
    base_url=f"http://{llm_endpoint}/v1",
    api_key="EMPTY"
)

# Main function to test the LLM client
async def main():
    # List available models from the LLM client
    print(await client.models.list())

    start = time.perf_counter()

    # Stream chat completions from the LLM
    async with client.chat.completions.stream(
        model=llm_model, # type: ignore
        messages=[
            {"role": "user", 
             "content": "Tell me about yourself."
             }
        ],
        max_tokens=3000,
        temperature=1.0,
        stream_options={"include_usage": True},
    ) as stream:
        async for event in stream:
            if event.type == "content.delta":
                print(event.delta, end="", flush=True)

    elapsed = time.perf_counter() - start
    print(f"\nElapsed time: {elapsed:.2f} seconds")

    #can call images an videous using this bellow message:
    # messages=[
    #     {
    #         "role": "user",
    #         "content": [
    #             {
    #                 "type": "image_url",
    #                 "image_url": {
    #                     "url": "https://github.com/oreakinodidi98/GenAIAgents/blob/main/ACA/ACA_GPU/images/PlatformCon-220.jpg?raw=true"
    #                 },
    #             },
    #             {
    #                 "type": "text", 
    #                 "text": "Summarize what happens in this video."
    #              },
    #         ],
    #     }
    # ],
    # Token consumption is available on the final completion
    completion = await stream.get_final_completion()
    usage = completion.usage
    completion_tokens = usage.completion_tokens if usage is not None else 0
    tokens_per_second = completion_tokens / elapsed if elapsed > 0 else 0
    print("\n\n--- Token usage ---")
    print(f"Prompt tokens:     {usage.prompt_tokens if usage is not None else 'unavailable'}")
    print(f"Completion tokens: {completion_tokens if usage is not None else 'unavailable'}")
    print(f"Total tokens:      {usage.total_tokens if usage is not None else 'unavailable'}")
    print(f"Elapsed time:      {elapsed:.2f} s")
    print(f"Throughput:        {tokens_per_second:.2f} tokens/s")


asyncio.run(main())