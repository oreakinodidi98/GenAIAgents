from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pprint import pprint


load_dotenv()

# initialise a model
model = init_chat_model(model="gpt-5-nano")
# invoke the model with a prompt and get response
response = model.invoke("What's the capital of the Moon?")

response
# print the response
print(response.content)
pprint(response.response_metadata)