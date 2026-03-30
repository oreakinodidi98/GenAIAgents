# Microsoft Agent Framework

## Autogen

- Multiple llm agents talking to each other and collaborating to solve problems

## Semantic kernel

- Open Source SDK
- More production ready
- But singe agents
- AI as a function call

## Microsoft agent framework

- Unifies both into single framework
- Open source SDK
- Build orchestra and deploy ai agents and multi agent workflows

## Ai agent

- Software that can perceive it’s environment, reason about it and take action towards its goals
- Task -> percieve your request
- React -> reason + act
- LLM think in a structured way to plan your next step
- Agent have tools to allow LLM to act on environment

## Process:Install dependencies, create a virtual environment, and create an environment variables file

1. Create AI Foundry Resource and project in Azure AI Foundry
   1. Assign the 'Cognitive Services OpenAI User' role to the search service identity.
2. Create an Azure AI Search service
   1. Navigate to your search service once it is created. Under Settings > Keys, ensure 'Both' is selected for API access control. Click save.
   2. Navigate to Settings > Identity > turn on system-assigned identity and click save.
   3. Assign two roles to your AI Foundry project's managed identity: the 'Search Index Data Reader' role and the 'Search Service Contributor' role
3. Create a chat model deployment in your AI project
4. Create an embedding model
5. Create a Storage Account
   1. Assign the 'Storage Blob Data Reader role' to the search service identity
6. Create a Grounding with Bing Search service
7. Set up Virtual enviroment ```python -m venv venv``` then ```venv\Scripts\activate```
8. Install needed packages insall ```pip install agent-framework```pip install -q langchain langchain_experimental openai python-dotenv langchain_openai```
9. install requirements package ```pip install -r requirements.txt```
10. Creates your .env file
    1. 'AIPROJECT_ENDPOINT' in your .env with your Azure AI Foundry project endpoint and 'AZURE_AI_API_KEY' with your API key, both of which can found in the the Overview page of your project
11. Create Azure AI Search Index
    1. Connect to you Azure AI Search service in AI foundry
    2. Upload documents to Azure Blob Storage, which Azure AI search connects to
    3. need an embedding model in order to convert our documents into vectors that will be stored in Azure AI Search
    4. vectorize our documents
    5. Connect on AI foundry