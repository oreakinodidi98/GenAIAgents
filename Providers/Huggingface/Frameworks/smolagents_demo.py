import os

from dotenv import load_dotenv
from huggingface_hub import login
from smolagents import CodeAgent, InferenceClientModel, tool


load_dotenv()

hf_token = os.getenv("HF_TOKEN")

if hf_token:
	login(token=hf_token)


@tool
def get_party_theme(guest_count: int) -> str:
	"""Suggest a party theme based on guest count.

	Args:
		guest_count: Number of expected guests.
	"""
	if guest_count < 10:
		return "Jazz lounge with a small curated playlist."
	if guest_count < 30:
		return "Retro dance set with a mix of pop and funk."
	return "High-energy party mix with crowd-pleasing anthems."


agent = CodeAgent(
	tools=[get_party_theme],
	model=InferenceClientModel(),
)

result = agent.run(
	"Suggest a party music direction for 24 guests at Wayne Manor."
)
print(result)