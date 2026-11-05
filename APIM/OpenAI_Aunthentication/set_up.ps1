# Generate a random number
$RAND = Get-Random
# Set it as an environment variable
$env:RAND = $RAND
# Print the random resource identifier
Write-Output "Random resource identifier will be: $RAND"
#set name suffix
$env:NAME_SUFFIX = "$RAND"
Write-Output "Name suffix set to: $env:NAME_SUFFIX"
# Create short suffix (first 6 characters) for resource names with length limits
$SHORT_SUFFIX = $env:NAME_SUFFIX.Substring(0, [Math]::Min(6, $env:NAME_SUFFIX.Length))
$RG = "rg-apim-genai-openai-$env:NAME_SUFFIX"
$location = "swedencentral"
$aiServiceName = "ai-genai-openai-$env:NAME_SUFFIX"
$apimName = "apim-genai-openai-$env:NAME_SUFFIX"

# create Azure resource group
az group create --name $RG --location $location

# create Azure AI services
az cognitiveservices account create -n $aiServiceName -g $RG `
   --kind AIServices `
   --sku S0 `
   --location $location `
   --custom-domain $aiServiceName

# create deployment for Chat GPT 6-sol model -> can update to latest model
az cognitiveservices account deployment create -n $aiServiceName -g $RG `
    --deployment-name gpt-6-sol `
    --model-name gpt-6-sol `
    --model-version "2026-09-22" `
    --model-format OpenAI `
    --sku-capacity "100" `
    --sku-name "GlobalStandard"

# create API Management with Comsumption mode, update email to yours
az apim create --name $apimName --resource-group $RG --location $location `
        --sku-name Consumption `
        --publisher-email "noreply@microsoft.com" `
        --publisher-name "Microsoft" `
        --enable-managed-identity

# create role assignment for API Management to access Azure AI Services
$apimIdentityPrincipalId = $(az apim show --name $apimName --resource-group $RG --query identity.principalId -o tsv)
$aiServicesResourceId = $(az cognitiveservices account show --name $aiServiceName --resource-group $RG --query id -o tsv)

az role assignment create --role "Cognitive Services OpenAI User" `
        --assignee $apimIdentityPrincipalId `
        --scope $aiServicesResourceId

# import specification for Microsoft Foundry to API Management
$aiServiceUrl = $(az cognitiveservices account show -n $aiServiceName -g $RG --query properties.endpoint -o tsv)
Write-Output " You have to import specification for Microsoft Foundry to API Management using the portal"

# Add authentication to the policy
# Not supported in Azure CLI, use Azure Portal or ARM template
# Use the policy in file policy.xml

# create subscription for API Management
# Not supported in Azure CLI, use Azure Portal or ARM template

# test the API: chatting with Chat GPT 6-sol model