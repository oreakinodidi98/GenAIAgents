from xmlrpc import client
from dotenv import load_dotenv
import os
import json
import asyncio
from azure.identity import AzureCliCredential,DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from agent_framework.azure import AzureOpenAIResponsesClient

load_dotenv() # Load environment variables from .env file
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_AI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_AI_CHAT_DEPLOYMENT_NAME")

# aunthenticate to entra
credentials= DefaultAzureCredential()
#connect to azure keyvault
key_vault_url = os.getenv("AZURE_KEY_VAULT_URL")
secret_client = SecretClient(vault_url=key_vault_url, credential=credentials)
#retrieve secrets from keyvault
secret_name= os.getenv("AZURE_OPENAI_SECRET_NAME")
secret = secret_client.get_secret(secret_name)
#store value of secret into a variable
sub_key=secret.value
print("Retrieved secret from Key Vault that starts with these characters." + sub_key[:5])


async def main():
   # initialise a response agent with azure openai response
   agent = AzureOpenAIResponsesClient(
         endpoint=AZURE_OPENAI_ENDPOINT,
         api_key=AZURE_OPENAI_KEY,
         deployment_name=AZURE_OPENAI_DEPLOYMENT
).create_agent(
        model=AZURE_OPENAI_DEPLOYMENT,
        name="demo-agent",
        instructions="You are a helpful agent that responds to user queries.",
)
   print(f"Created agent with ID: {agent.id}")
   print(await agent.run("Hello, can you provide a brief overview of Azure AI services?"))

if __name__ == "__main__":
    asyncio.run(main())
