# Project overview

1. Build a modern, production-ready multi-agent system using the latest Azure AI Python SDKs and best practices
2. Each agent is created as a connected agent using Azure AI Agent Service.
3. Orchestration is performed using direct agent-to-agent calls, not just a group chat or plugin pattern.
4. Uses official Microsoft documentation patterns for agent creation, tool/resource registration, and message passing.
5. The multi-agent system we create will consist of 3 agents that work together to generate detailed reports about health insurance policy documents, 

**Orchestration logic:**

- **Search Agent** - This agent will search Azure AI Search index for information.
- **Report Agent** - This agent will generate a detailed report based on the information returned from the Search Agent.
- **Validation Agent** - This agent will validate that the generated report meets specified requirements. In our case, making sure that the report contains information about coverage exclusions.
- Orchestrator logic - we use direct orchestration logic written in Python to coordinate the three agents (Search, Report, Validation) using the Azure AI Agent Service SDK.

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
8. Install needed packages insall ```pip install -q langchain langchain_experimental openai python-dotenv langchain_openai```
9. install requirements package ```pip install -r requirements.txt```
10. Creates your .env file
    1. 'AIPROJECT_ENDPOINT' in your .env with your Azure AI Foundry project endpoint and 'AZURE_AI_API_KEY' with your API key, both of which can found in the the Overview page of your project
11. Create Azure AI Search Index
    1. Connect to you Azure AI Search service in AI foundry
    2. Upload documents to Azure Blob Storage, which Azure AI search connects to
    3. need an embedding model in order to convert our documents into vectors that will be stored in Azure AI Search
    4.  vectorize our documents
    5.  Connect on AI foundry

## Auto multi agent

1. This section demonstrates how to use an AgentTeam to execute a multi-step, user request with automatic function calling and trace collection.
2. The team consists of
   1. One leader agent - created automatically from the configuration in `utils/agent_team_config.yaml`
   2. three worker agents - `TimeWeatherAgent`, `SendEmailAgent`, and `TemperatureAgent`, each defined in the code below with its own tools
3. Create `utils/agent_team_config.yaml` folder
4. `utils/agent_team_config.yaml` contains the key ```TEAM_LEADER_MODEL```. Its value must be the name of a **deployed** model in your Azure AI project (e.g. "gpt-4o-mini")
5. pip install azure-ai-projects azure-ai-agents azure-identity
6. Set these environment variables with values:
7. PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview page of your Azure AI Foundry portal.
8. MODEL_DEPLOYMENT_NAME - The model deployment name used for the worker agents.