from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pprint import pprint
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.messages import AIMessage


load_dotenv()

# initialise a model, with customization
model = init_chat_model(
    model="gpt-5-nano",
    # Kwargs passed to the model:
    temperature=1.0
    )

# initialise an agent
agent = create_agent(model = model)

# invoke the agent with a prompt and get response
response = agent.invoke(HumanMessage(content="What's the capital of the Moon?"))

# print the response
pprint(response)
# to get the content of the last message in the response which is actually the answer to the question
print(response['messages'][-1].content)
