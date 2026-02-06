from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pprint import pprint
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from pydantic import BaseModel

# create class to structure output of the agent
class CapitalInfo(BaseModel):
    name: str
    location: str
    vibe: str
    economy: str

load_dotenv()

# initialise a model, with customization
model = init_chat_model(
    model="gpt-5-nano",
    # Kwargs passed to the model:
    temperature=1.0
    )

# create system prompt
system_prompt = "You are a science fiction writer, create a capital city at the users request."

# initialise an agent with system prompt and output parser to structure the output in the form of CapitalInfo class
agent = create_agent(model = model,
                     system_prompt=system_prompt,
                     response_format=CapitalInfo
)

# invoke the agent with a prompt and get response 
question = HumanMessage(content="What's the capital of the moon?")

response = agent.invoke(
    {"messages": [question]}
)

capital_info = response["structured_response"]

capital_name = capital_info.name
capital_location = capital_info.location

print(f"{capital_name} is a city located at {capital_location}")

