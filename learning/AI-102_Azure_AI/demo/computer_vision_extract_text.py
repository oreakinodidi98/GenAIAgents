from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import time

'''
References:
    Quickstart: https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts-sdk/python-sdk
    SDK: https://docs.microsoft.com/en-us/python/api/overview/azure/cognitiveservices/computervision?view=azure-python
    Key Vault: https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-python
'''

# Replace with your endpoint and key from the Azure portal
endpoint = 'https://azureaicoursedemooa.cognitiveservices.azure.com/'
# key = '<ADD COMPUTER VISION SUBSCRIPTION KEY HERE>'

# ===== Alternatively, uncomment and get endpoint/key from environment variables =====

'''
# import os
# endpoint = os.environ['COMPUTER_VISION_ENDPOINT']
# key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
'''

# ===== Key Vault Configuration =====
KEYVAULT_URL = "https://oaaidemoazurecr-kv.vault.azure.net/"  # Replace with your Key Vault name
SECRET_KEY_NAME = "azureaicoursedemoOA"

# Initialize Key Vault client using DefaultAzureCredential (uses Azure CLI login, managed identity, etc.)
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)

# Retrieve secrets from Key Vault
try:
    key = secret_client.get_secret(SECRET_KEY_NAME).value
    print(f"✓ Secrets loaded from Key Vault successfully")
except Exception as e:
    print(f"✗ Failed to retrieve secrets from Key Vault: {e}")
    raise
    
# Set credentials
credentials = CognitiveServicesCredentials(key)

# Create client
client = ComputerVisionClient(endpoint, credentials)

url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/printed_text.jpg"
numberOfCharsInOperationId = 36

# Async SDK call (new Read API)
rawHttpResponse = client.read(url, raw=True)

# Get ID from returned headers
operationLocation = rawHttpResponse.headers["Operation-Location"]
idLocation = len(operationLocation) - numberOfCharsInOperationId
operationId = operationLocation[idLocation:]

# Poll for completion
while True:
    result = client.get_read_result(operationId)
    if result.status not in [OperationStatusCodes.not_started, OperationStatusCodes.running]:
        break
    time.sleep(1)

# Get data: displays text captured and its bounding box (position in the image)
if result.status == OperationStatusCodes.succeeded:
    for textResult in result.analyze_result.read_results:
        for line in textResult.lines:
            print(line.text)
            print(line.bounding_box)