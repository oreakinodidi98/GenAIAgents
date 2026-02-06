from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pprint import pprint
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from pydantic import BaseModel
from langchain.tools import tool


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
system_prompt = "You are an arithmetic wizard. Use your tools to calculate the square root and square of any number."

# create a tool decorator function which takes in a number and returns its square root
@tool("square_root", description="Calculate the square root of a number")
def tool1(x: float) -> float:
    return x ** 0.5

# initialise an agent with system prompt and tool
agent = create_agent(model = model,
                     system_prompt=system_prompt,
                     tools=[tool1]
)

# invoke the agent with a prompt and get response 
question = HumanMessage(content="Calculate the square root of 16.")

response = agent.invoke(
    {"messages": [question]}
)

pprint(response['messages'])
print(response['messages'][-1].content)
print(response["messages"][1].tool_calls)
