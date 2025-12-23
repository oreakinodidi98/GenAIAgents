# Azure container apps deployment script

# Generate a random number
$RAND = Get-Random

# Set it as an environment variable
$env:RAND = $RAND

# Print the random resource identifier
Write-Output "Random resource identifier will be: $RAND"
# Parameters
$env:LOCATION = 'uksouth'
$env:ACA_RG="rg-agents"
$env:ACA_ENV="agents-env"
$env:ACA_NAME="aca-agent-framework"

# create resource group 
az group create --name $env:ACA_RG --location $env:LOCATION
Write-Output "Resource group $env:ACA_RG created"
# create container apps environment
az containerapp env create `
  --name $env:ACA_ENV `
  --resource-group $env:ACA_RG `
  --location $env:LOCATION
Write-Output "Container Apps environment $env:ACA_ENV created"
# create container app
az containerapp up `
  --name $env:ACA_NAME `
  --resource-group $env:ACA_RG `
  --environment $env:ACA_ENV `
  --source ./academo `
  --cpu 0.5 `
  --memory 1.0Gi `
  --ingress 'external' `
  --target-port 8080 `
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
# Create Application Insights resource
Write-Output "Creating Application Insights resource: agent-framework-ai"
az monitor app-insights component create `
  --app "agent-framework-ai" `
  --location $env:LOCATION `
  --resource-group $env:ACA_RG `
  --application-type "web"
#applicaationinsights connection string
$env:APPLICATIONINSIGHTS_CONNECTION_STRING = az monitor app-insights component show `
  --app "agent-framework-ai" `
  --resource-group $env:ACA_RG `
  --query "connectionString" -o tsv
# End of script