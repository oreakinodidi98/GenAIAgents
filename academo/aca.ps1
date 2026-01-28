# Azure container apps deployment script

# Generate a random number
$RAND = Get-Random

# Set it as an environment variable
$env:RAND = $RAND

# Print the random resource identifier
Write-Output "Random resource identifier will be: $RAND"
# Parameters
$env:LOCATION = 'uksouth'
$env:ACA_RG="demo-rg-agents-$RAND"
$env:ACA_ENV="agents-env"
$env:ACA_NAME="aca-agent-framework"
$env:WORKSPACE_NAME="ws-agent-framework-$RAND"
$env:APP_INSIGHTS_NAME="ai-agent-framework-$RAND"
$env:CONTAINER_REGISTRY_NAME="acragentframework$RAND"
$env:MANAGED_IDENTITY_NAME="mi-agent-framework-$RAND"
$env:AZURE_AI_ACCOUNT_NAME="aia-agent-framework-$RAND"
$env:AZURE_AI_PROJECT_NAME="aip-agent-framework-$RAND"
$env:CONTAINER_IMAGE="mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"

# create resource group 
az group create --name $env:ACA_RG --location $env:LOCATION
Write-Output "Resource group $env:ACA_RG created"

# Create Log Analytics Workspace
Write-Output "Creating Log Analytics Workspace: $env:WORKSPACE_NAME"
az monitor log-analytics workspace create `
  --resource-group $env:ACA_RG `
  --workspace-name $env:WORKSPACE_NAME `
  --location $env:LOCATION `
  --retention-time 30
$env:WORKSPACE_RESOURCE_ID = az monitor log-analytics workspace show `
  --resource-group $env:ACA_RG `
  --workspace-name $env:WORKSPACE_NAME `
  --query "id" -o tsv
$env:WORKSPACE_CUSTOMER_ID = az monitor log-analytics workspace show `
  --resource-group $env:ACA_RG `
  --workspace-name $env:WORKSPACE_NAME `
  --query "customerId" -o tsv
$env:WORKSPACE_KEY = az monitor log-analytics workspace get-shared-keys `
  --resource-group $env:ACA_RG `
  --workspace-name $env:WORKSPACE_NAME `
  --query "primarySharedKey" -o tsv

# Create Application Insights resource
Write-Output "Creating Application Insights resource: agent-framework-ai"
az monitor app-insights component create `
  --app $env:APP_INSIGHTS_NAME `
  --location $env:LOCATION `
  --resource-group $env:ACA_RG `
  --workspace $env:WORKSPACE_RESOURCE_ID `
#applicaationinsights connection string
$env:APPLICATIONINSIGHTS_CONNECTION_STRING = az monitor app-insights component show `
  --app $env:APP_INSIGHTS_NAME `
  --resource-group $env:ACA_RG `
  --query "connectionString" -o tsv

# create container registry
Write-Output "Creating Container Registry: $env:CONTAINER_REGISTRY_NAME"
az acr create `
  --resource-group $env:ACA_RG `
  --name $env:CONTAINER_REGISTRY_NAME `
  --sku Standard `
  --location $env:LOCATION `
  --admin-enabled false `
  --public-network-enabled true
$env:ACR_LOGIN_SERVER = az acr show `
  --name $env:CONTAINER_REGISTRY_NAME `
    --resource-group $env:ACA_RG `
    --query "loginServer" -o tsv
Write-Output "Container Registry: $env:ACR_LOGIN_SERVER"

# create user assigned managed identity
Write-Output "Creating User Assigned Managed Identity: $env:MANAGED_IDENTITY_NAME"
az identity create `
  --name $env:MANAGED_IDENTITY_NAME `
  --resource-group $env:ACA_RG `
  --location $env:LOCATION
$env:MANAGED_IDENTITY_ID = az identity show `
  --name $env:MANAGED_IDENTITY_NAME `
    --resource-group $env:ACA_RG `
    --query "id" -o tsv
$env:MANAGED_IDENTITY_CLIENT_ID = az identity show `
  --name $env:MANAGED_IDENTITY_NAME `
    --resource-group $env:ACA_RG `
    --query "clientId" -o tsv
$env:MANAGED_IDENTITY_PRINCIPAL_ID = az identity show `
  --name $env:MANAGED_IDENTITY_NAME `
    --resource-group $env:ACA_RG `
    --query "principalId" -o tsv

    # wait for identity to be ready
Start-Sleep -Seconds 30

# assign acr pull role to managed identity

az role assignment create `
  --assignee-object-id $env:MANAGED_IDENTITY_PRINCIPAL_ID `
  --assignee-principal-type ServicePrincipal `
  --role "AcrPull" `
  --scope $(az acr show --name $env:CONTAINER_REGISTRY_NAME --resource-group $env:ACA_RG --query "id" -o tsv)
Write-Output "Assigned AcrPull role to Managed Identity: $env:MANAGED_IDENTITY_NAME"

# create Azurre AI resources (optional)
Write-Output "Creating Azure AI resources"
az cognitiveservices account create `
  --name $env:AZURE_AI_ACCOUNT_NAME `
  --resource-group $env:ACA_RG `
  --location $env:LOCATION `
  --kind AIServices `
  --sku S0 `
  --yes
$env:AZURE_AI_ACCOUNT_ID = az cognitiveservices account show `
  --name $env:AZURE_AI_ACCOUNT_NAME `
  --resource-group $env:ACA_RG `
  --query "id" -o tsv
# get endpoint
$env:AZURE_AI_ACCOUNT_ENDPOINT = az cognitiveservices account show `
  --name $env:AZURE_AI_ACCOUNT_NAME `
  --resource-group $env:ACA_RG `
  --query "properties.endpoint" -o tsv
# Assign Cognitive Services User role to the managed identity
az role assignment create `
  --assignee-object-id $env:MANAGED_IDENTITY_PRINCIPAL_ID `
  --assignee-principal-type ServicePrincipal `
  --role "Cognitive Services User" `
  --scope $env:AZURE_AI_ACCOUNT_ID

# create container apps environment
az containerapp env create `
  --name $env:ACA_ENV `
  --resource-group $env:ACA_RG `
  --location $env:LOCATION `
  --logs-workspace-id $env:WORKSPACE_CUSTOMER_ID `
  --logs-workspace-key $env:WORKSPACE_KEY `
  --tags "azd-env-name=$env:RAND"
Write-Output "Container Apps environment $env:ACA_ENV created"
# create container app
az containerapp create `
  --name $env:ACA_NAME `
  --resource-group $env:ACA_RG `
  --environment $env:ACA_ENV `
  --image $env:CONTAINER_IMAGE `
  --cpu 0.5 `
  --memory 1.0Gi `
  --min-replicas 0 `
  --max-replicas 3 `
  --ingress 'external' `
  --target-port 8080 `
  --registry-server $env:ACR_LOGIN_SERVER `
  --registry-identity $env:MANAGED_IDENTITY_ID `
  --secrets "app-insights-connection=$env:APPLICATIONINSIGHTS_CONNECTION_STRING" `
  --user-assigned $env:MANAGED_IDENTITY_ID `
  --env-vars `
    AZURE_AI_PROJECT_ENDPOINT=$env:AZURE_AI_PROJECT_ENDPOINT `
    AZURE_AI_MODEL_DEPLOYMENT_NAME=$env:AZURE_AI_MODEL_DEPLOYMENT_NAME `
    APPLICATIONINSIGHTS_CONNECTION_STRING=$env:APPLICATIONINSIGHTS_CONNECTION_STRING
Write-Output "Container App $env:ACA_NAME created and deployed"
# show container app url
$ACA_URL = az containerapp show `
  --name $env:ACA_NAME `
  --resource-group $env:ACA_RG `
  --query "properties.configuration.ingress.fqdn" -o tsv
Write-Output "Container App URL: https://$ACA_URL"
Write-Output "You can now access the agent at: https://$ACA_URL"

Write-Output ""
Write-Output "========================================" 
Write-Output "Deployment Complete!"
Write-Output "========================================" 
Write-Output "Container App URL: https://$ACA_URL"
Write-Output "Health Check: https://$ACA_URL/healthz"
Write-Output "Azure AI Endpoint: $env:AZURE_AI_PROJECT_ENDPOINT"
Write-Output ""
Write-Output "Next Steps:"
Write-Output "1. Build your image: az acr build --registry $env:CONTAINER_REGISTRY_NAME --image agentapp:latest ."
Write-Output "2. Update container: az containerapp update --name $env:ACA_NAME --resource-group $env:ACA_RG --image $env:ACR_LOGIN_SERVER/agentapp:latest"
Write-Output ""

# Save deployment info
@"
Deployment Information
======================
Resource Group: $env:ACA_RG
Container App: $env:ACA_NAME
App URL: https://$ACA_URL
Container Registry: $env:ACR_LOGIN_SERVER
Managed Identity: $env:MANAGED_IDENTITY_NAME
  Client ID: $env:MANAGED_IDENTITY_CLIENT_ID
  Principal ID: $env:MANAGED_IDENTITY_PRINCIPAL_ID
Azure AI Account: $env:AZURE_AI_ACCOUNT_NAME
Azure AI Endpoint: $env:AZURE_AI_PROJECT_ENDPOINT
App Insights: $env:APP_INSIGHTS_NAME
Connection String: $env:APPLICATIONINSIGHTS_CONNECTION_STRING

Build Command:
az acr build --registry $env:CONTAINER_REGISTRY_NAME --image agentapp:latest .

Update Command:
az containerapp update --name $env:ACA_NAME --resource-group $env:ACA_RG --image $env:ACR_LOGIN_SERVER/agentapp:latest

Generated on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@ | Out-File -FilePath "deployment-output.txt" -Encoding UTF8

Write-Output "Deployment details saved to: deployment-output.txt"

# End of script