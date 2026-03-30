import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import ResponseStreamEventType

load_dotenv()

# check env variables are loaded
print(f"Foundry Endpoint: {os.getenv('AZURE_AI_FOUNDRY_PROJECT_ENDPOINT')}")
print(f"Foundry Name: {os.getenv('AZURE_AI_FOUNDRY_NAME')}")

# set agent name
agent_name=os.getenv('AZURE_AI_FOUNDRY_NAME')
endpoint=os.getenv('AZURE_AI_FOUNDRY_PROJECT_ENDPOINT')

# set project client
project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
)

#set open ai client
openai_client = project_client.get_openai_client()


def main():
    
    # set conversation
    conversation = openai_client.conversations.create()
    print(f"Created conversation with id: {conversation.id}")
    
    # set input data
    input_data = """
    "id": "email_002",
        "order_number": null,
        "body": "Hi,\n\nI’m contacting you regarding the closure I recently received. Based on standard measuring methods used in the hair industry, this unit does not appear to be a full 7x7. The lace coverage is smaller once the edges are excluded.\n\nCould you clarify how your measurements are taken?\n\nBest regards,"
    """
    # set stream
    stream = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent":{"name": agent_name, "type": "agent_reference"}},
        stream=False,
        input=input_data,
        metadata={"x-ms-debug-mode-enabled": "1"}
    )
    # print response
    print(f"Resonse Output: {stream.output_text}")
    # print("Response from Foundry AI Agent:")

    # for response in stream:
    #     if response.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DONE:
    #         print("\t", response.text)
    #     elif response.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED and response.item.type == "workflow_action":
    #         print(f"********\nActor - '{response.item.action_id}' :")
    #     elif response.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED and response.item.type == "workflow_action":
    #         print(f"Worflow Item '{response.item.action_id}' is '{response.item.status}' - (previous item was : '{response.item.previous_action}).")
    #     elif response.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE and response.item.type == "workflow_action":
    #         print(f"Worflow Item '{response.item.action_id}' is '{response.item.status}' - (previous item was : '{response.item.previous_action}).")
    #     elif response.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DELTA:
    #         print("Delta:" + response.delta)
    #     else:
    #         print(f"Unrecognized response type: {response}")

    # close conversation
    openai_client.conversations.delete(conversation.id)
    print(f"Deleted conversation with id: {conversation.id}")

if __name__ == "__main__":
    main()
