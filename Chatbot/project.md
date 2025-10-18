# Project overview

1. Create Chat bot Locally
2. Docker container
3. Take to ACR
4. Deploy to ACI 

## process

1. Set up Virtual enviroment ```python -m venv agent_env``` then ```agent_env\Scripts\activate```
2. Install needed packages insall ```pip install -q langchain langchain_experimental openai python-dotenv langchain_openai```
3. install requirements package ```pip install -r requirements.txt```
4. Go to frontend use ```pnpm run setup``` to build main app inside API folder )API-> Static -> react -> assets)
   1. Install pnpm via npm (if you have Node.js installed) ```npm install -g pnpm```
5. use ```azd login``` for developer credentials
   1. Install Azure Developer CLI ```winget install microsoft.azd```
   2. Verify azd is installed ```azd version```
   3. Login to Azure (this will open browser for authentication ```azd login```
   4. Verify login status ```azd auth login-status```
6. Run with uvicorn for development ```uvicorn api.main:create_app --factory --host 0.0.0.0 --port 8000 --reload```
7. need to give mysef role of ```Search Index Data Reader``` in azure for search
8. Build dockerfile using ```docker build -t <name:latest> .```
9. Run dockerfile -> called it ai-chat-demo:latest so ```docker run -p 8082:50505 ai-chat-demo:latest```
   1. should fail as image has no access to all the keys in env file -> need a docker-compose file
   2. change log in to use keys instead of azd on main.py
10. Now ```docker compose up``` to run container locally
    1. ```docker compose down``` to remove if it fails
    2. ```docker images``` to see image built
11. Deploy to ACR
    1. Need ACR pull and ACR push
    2. Build dockerfile using ```docker build -t oaaidemo.azurecr.io/ai-chat-demo:latest .```
    3. Login to registry ```az acr login --name $ACR_NAME```
    4. push with ```docker push $ACR_NAME/ai-chat-demo:latest```
    5. optional can rebuild on platform amd64 using ```docker buildx build --platform linux/amd64 -t $ACR_NAME/ai-chat-demo:latest .```
    6. Create KV
    7. Create SP with ACR pull
    8. $ACR_NAME = "oaaidemo"
    9. $KV_NAME = "oaaidemoazurecr-kv"
    10. $SP_NAME = "oaaidemo-acr-pull-sp"
    11. $ROLE = "AcrPull"
    12. $ACR_ID = az acr show --name $ACR_NAME --query id --output tsv
    13. Create service principal with ACR pull permission
        1. $SP_CREDENTIALS = az ad sp create-for-rbac --name $SP_NAME --scopes $ACR_ID --role $ROLE --output json | ConvertFrom-Json
    14. Extract the values
        1. $SP_APP_ID = $SP_CREDENTIALS.appId
        2. $SP_PASSWORD = $SP_CREDENTIALS.password
    15. Store service principal app ID
         1. az keyvault secret set --vault-name $KV_NAME --name "acr-pull-sp-id" --value $SP_APP_ID
    16. Store service principal password
        1. az keyvault secret set --vault-name $KV_NAME --name "acr-pull-sp-password" --value $SP_PASSWORD
    17. Store ACR login server
         1. az keyvault secret set --vault-name $KV_NAME --name "acr-login-server" --value "$ACR_NAME.azurecr.io"
    18. set roles ```az role assignment create --assignee $SP_APP_ID --scope $ACR_ID --role $ROLE```
12. Create log analytics workspace
    1. Get workspace ID
    2. Get workspace Key
13. Create **user assighned Managed identity for Production**
    1. Store Cliend ID as env Variables -> store in kv -> ```az keyvault secret set --vault-name $KV_NAME --name "azure-client-id" --value "" ```
    2. Set $USER_IDENTITY_ID -> can get from JSON view = ID
    3. Set role as cognitive services user
    4. Get search service resource ID
       1. $SEARCH_SERVICE_ID = az search service show --resource-group $RESOURCE_GROUP --name "your-search-service-name" --query id --output tsv
    5. Get managed identity principal ID
       1. $USER_IDENTITY_PRINCIPAL_ID = az identity show --resource-group $RESOURCE_GROUP --name "your-managed-identity-name" --query principalId --output tsv
    6. Assign required roles
       1. ```az role assignment create --assignee $USER_IDENTITY_PRINCIPAL_ID --scope $SEARCH_SERVICE_ID --role "Search Index Data Reader"```
       2. ```az role assignment create --assignee $USER_IDENTITY_PRINCIPAL_ID --scope $SEARCH_SERVICE_ID --role "Search Index Data Contributor"```
14. Put **ENV Keys into KV** ```az keyvault secret set --vault-name $KV_NAME --name "azure-openai-api-key" --value```
    1. Store AI Project settings: `az keyvault secret set --vault-name $KV_NAME --name "azure-aiproject-endpoint" --value "..."`
    2. Store search settings: `az keyvault secret set --vault-name $KV_NAME --name "azure-search-endpoint" --value "..."`
    3. Store all secrets: Use the complete script above
    4. Verify: `az keyvault secret list --vault-name $KV_NAME --query "[].name" --output table`
    5. CLiendtID of Managed ID in KV
15. Deploy to **ACI **so others can see it
    1. $RESOURCE_GROUP = "AI_Demo"
    2. $KV_NAME = "oaaidemoazurecr-kv"
    3. $CONTAINER_NAME = "ai-chatbot-aci"
    4. $ACR_SP_ID = az keyvault secret show --vault-name $KV_NAME --name "acr-pull-sp-id" --query value --output tsv
    5. $ACR_SP_PASSWORD = az keyvault secret show --vault-name $KV_NAME --name "acr-pull-sp-password" --query value --output tsv
    6. $ACR_LOGIN_SERVER = az keyvault secret show --vault-name $KV_NAME --name "acr-login-server" --query value --output tsv
    7. $WORKSPACE_ID = az monitor log-analytics workspace show --resource-group $RESOURCE_GROUP --workspace-name "aicontainerdemo" --query customerId --output tsv
    8. $WORKSPACE_KEY = az monitor log-analytics workspace get-shared-keys --resource-group $RESOURCE_GROUP --workspace-name "aicontainerdemo" --query primarySharedKey --output tsv

```
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --image "$ACR_LOGIN_SERVER/ai-chat-demo:latest" \
  --registry-login-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_SP_ID \
  --registry-password $ACR_SP_PASSWORD \
  --dns-name-label "ai-chatbot-demo-$(Get-Random -Maximum 9999)" \
  --ports 50505 \
  --cpu 1 \
  --memory 2 \
  --os-type Linux \
  --restart-policy Always \
  --log-analytics-workspace $WORKSPACE_ID \
  --log-analytics-workspace-key $WORKSPACE_KEY \
  --assign-identity $USER_IDENTITY_ID \
  --environment-variables \
    RUNNING_IN_PRODUCTION=true \
    PORT=80 \
    AZURE_CLIENT_ID="$(az keyvault secret show --vault-name $KV_NAME --name azure-client-id --query value -o tsv)" \
    AZURE_EXISTING_AIPROJECT_ENDPOINT="$(az keyvault secret show --vault-name $KV_NAME --name azure-aiproject-endpoint --query value -o tsv)" \
    AZURE_EXISTING_AIPROJECT_ENDPOINT_API_KEY="$(az keyvault secret show --vault-name $KV_NAME --name azure-aiproject-api-key --query value -o tsv)" \
    AZURE_AI_CHAT_DEPLOYMENT_NAME="$(az keyvault secret show --vault-name $KV_NAME --name azure-ai-chat-deployment --query value -o tsv)" \
    AZURE_AI_SEARCH_ENDPOINT="$(az keyvault secret show --vault-name $KV_NAME --name azure-search-endpoint --query value -o tsv)" \
    AZURE_AI_SEARCH_INDEX_NAME="$(az keyvault secret show --vault-name $KV_NAME --name azure-search-index-name --query value -o tsv)" \
    AZURE_SEARCH_API_KEY="$(az keyvault secret show --vault-name $KV_NAME --name azure-search-api-key --query value -o tsv)" \
    AZURE_TENANT_ID="$(az keyvault secret show --vault-name $KV_NAME --name azure-tenant-id --query value -o tsv)" \
    AZURE_AI_EMBED_DEPLOYMENT_NAME="$(az keyvault secret show --vault-name $KV_NAME --name azure-ai-embed-deployment --query value -o tsv)" \
    AZURE_AI_EMBED_DIMENSIONS="$(az keyvault secret show --vault-name $KV_NAME --name azure-ai-embed-dimensions --query value -o tsv)" \
  --query "{FQDN:ipAddress.fqdn}" \
  --output table
```

or 

```
az container create --resource-group $RESOURCE_GROUP --name "ai-chatbot-aci-$(Get-Random -Maximum 9999)" --image "$ACR_LOGIN_SERVER/ai-chat-demo:latest" --registry-login-server $ACR_LOGIN_SERVER --registry-username $ACR_SP_ID --registry-password $ACR_SP_PASSWORD --dns-name-label "ai-chatbot-demo-$(Get-Random -Maximum 9999)" --ports 80 --cpu 1 --memory 2 --os-type Linux --restart-policy Always --log-analytics-workspace $WORKSPACE_ID --log-analytics-workspace-key $WORKSPACE_KEY --assign-identity $USER_IDENTITY_ID --environment-variables RUNNING_IN_PRODUCTION=true PORT=80 AZURE_CLIENT_ID="$(az keyvault secret show --vault-name $KV_NAME --name azure-client-id --query value -o tsv)" AZURE_EXISTING_AIPROJECT_ENDPOINT="$(az keyvault secret show --vault-name $KV_NAME --name azure-aiproject-endpoint --query value -o tsv)" AZURE_EXISTING_AIPROJECT_ENDPOINT_API_KEY="$(az keyvault secret show --vault-name $KV_NAME --name azure-aiproject-api-key --query value -o tsv)" AZURE_AI_CHAT_DEPLOYMENT_NAME="$(az keyvault secret show --vault-name $KV_NAME --name azure-ai-chat-deployment --query value -o tsv)" AZURE_AI_SEARCH_ENDPOINT="$(az keyvault secret show --vault-name $KV_NAME --name azure-search-endpoint --query value -o tsv)" AZURE_AI_SEARCH_INDEX_NAME="$(az keyvault secret show --vault-name $KV_NAME --name azure-search-index-name --query value -o tsv)" AZURE_SEARCH_API_KEY="$(az keyvault secret show --vault-name $KV_NAME --name azure-search-api-key --query value -o tsv)" AZURE_TENANT_ID="$(az keyvault secret show --vault-name $KV_NAME --name azure-tenant-id --query value -o tsv)" AZURE_AI_EMBED_DEPLOYMENT_NAME="$(az keyvault secret show --vault-name $KV_NAME --name azure-ai-embed-deployment --query value -o tsv)" AZURE_AI_EMBED_DIMENSIONS="$(az keyvault secret show --vault-name $KV_NAME --name azure-ai-embed-dimensions --query value -o tsv)" --query "{FQDN:ipAddress.fqdn}" --output table
```