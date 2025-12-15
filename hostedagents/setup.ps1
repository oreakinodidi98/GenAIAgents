# Generate a random number
$RAND = Get-Random

# Set it as an environment variable
$env:RAND = $RAND

# Print the random resource identifier
Write-Output "Random resource identifier will be: $RAND"

# Parameters
$env:LOCATION = 'northcentralus'
Write-Output "Location set to: $env:LOCATION"

$env:FOUNDRY_ACCOUNT_NAME = "foundryaccount$RAND"  # Replace with your desired name
$env:PROJECT_NAME = "foundryproject$RAND"  # Replace with your desired name
$env:ACR_NAME = "myregistry$RAND"

# Create a resource group name using the random number
$env:RG_NAME = "myresourcegroup$RAND"
Write-Output "Resource group name: $env:RG_NAME"

# CREATE RESOURCE GROUP !
az group create --name $env:RG_NAME --location $env:LOCATION
Write-Output "Resource group $env:RG_NAME created"

# Create Container Registry
Write-Output "Creating Azure Container Registry: $env:ACR_NAME"
az acr create `
  --resource-group $env:RG_NAME `
  --name $env:ACR_NAME `
  --sku Standard `
  --location $env:LOCATION `
  --admin-enabled false `
  --public-network-enabled true

$env:ACR_ID = az acr show `
  --name $env:ACR_NAME `
  --resource-group $env:RG_NAME `
  --query "id" -o tsv

$env:ACR_LOGIN_SERVER = az acr show `
  --name $env:ACR_NAME `
  --resource-group $env:RG_NAME `
  --query "loginServer" -o tsv
Write-Output "Container Registry: $env:ACR_LOGIN_SERVER"

# Create Foundry Account
Write-Output "Creating Foundry Account: $env:FOUNDRY_ACCOUNT_NAME"

az cognitiveservices account create `
  --name $env:FOUNDRY_ACCOUNT_NAME `
  --resource-group $env:RG_NAME `
  --location $env:LOCATION `
  --kind AIServices `
  --sku S0 `
  --custom-domain $env:FOUNDRY_ACCOUNT_NAME `
  --assign-identity `
  --yes

Write-Output "Waiting for Foundry Account to be ready..."
Start-Sleep -Seconds 30

# Verify the account was created
$accountCheck = az cognitiveservices account show `
  --name $env:FOUNDRY_ACCOUNT_NAME `
  --resource-group $env:RG_NAME 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Output "ERROR: Foundry Account was not created successfully"
    Write-Output $accountCheck
    exit 1
}
Write-Output "AI Foundry Account created"

# Get the managed identity principal ID
$env:FOUNDRY_PRINCIPAL_ID = az cognitiveservices account identity show `
  --name $env:FOUNDRY_ACCOUNT_NAME `
  --resource-group $env:RG_NAME `
  --query "principalId" -o tsv

if ([string]::IsNullOrEmpty($env:FOUNDRY_PRINCIPAL_ID)) {
    Write-Output "ERROR: Could not get Foundry Principal ID"
    exit 1
}

Write-Output "Foundry Principal ID: $env:FOUNDRY_PRINCIPAL_ID"

# ===== CREATE AI PROJECT (Using REST API) =====
Write-Output "Creating AI Project: $env:PROJECT_NAME"

# Get access token
$env:ACCESS_TOKEN = az account get-access-token --query accessToken -o tsv
$env:SUBSCRIPTION_ID = az account show --query id -o tsv

# Create Project using REST API
$projectUrl = "https://management.azure.com/subscriptions/$env:SUBSCRIPTION_ID/resourceGroups/$env:RG_NAME/providers/Microsoft.CognitiveServices/accounts/$env:FOUNDRY_ACCOUNT_NAME/projects/$env:PROJECT_NAME`?api-version=2025-10-01-preview"

$projectBody = @{
    location = $env:LOCATION
    identity = @{
        type = "SystemAssigned"
    }
    properties = @{
        description = "$env:PROJECT_NAME Project"
        displayName = $env:PROJECT_NAME
    }
} | ConvertTo-Json -Depth 10

$headers = @{
    "Authorization" = "Bearer $env:ACCESS_TOKEN"
    "Content-Type" = "application/json"
}

try {
    $projectResult = Invoke-RestMethod -Uri $projectUrl -Method Put -Headers $headers -Body $projectBody
    Write-Output "AI Project created successfully"
} catch {
    Write-Output "Error creating AI Project: $($_.Exception.Message)"
    Write-Output $_.Exception.Response
}

# ===== CREATE AGENTS CAPABILITY HOST (Using REST API) =====
Write-Output "Creating Agents Capability Host"

$capabilityHostUrl = "https://management.azure.com/subscriptions/$env:SUBSCRIPTION_ID/resourceGroups/$env:RG_NAME/providers/Microsoft.CognitiveServices/accounts/$env:FOUNDRY_ACCOUNT_NAME/capabilityHosts/agents?api-version=2025-10-01-preview"

$capabilityBody = @{
    properties = @{
        capabilityHostKind = "Agents"
        enablePublicHostingEnvironment = $true
    }
} | ConvertTo-Json -Depth 10

try {
    Invoke-RestMethod -Uri $capabilityHostUrl -Method Put -Headers $headers -Body $capabilityBody
    Write-Output "Agents Capability Host created successfully"
} catch {
    Write-Output "Error creating Agents Capability Host: $_"
}

# ===== ASSIGN ACR PULL ROLE TO FOUNDRY IDENTITY =====
Write-Output "Assigning AcrPull role to AI Foundry managed identity"

# AcrPull role definition ID
$acrPullRoleId = "7f951dda-4ed3-4680-a7ca-43fe172d538d"

# Wait a bit for the identity to propagate
Start-Sleep -Seconds 15

az role assignment create `
  --assignee $env:FOUNDRY_PRINCIPAL_ID `
  --role $acrPullRoleId `
  --scope $env:ACR_ID

if ($LASTEXITCODE -eq 0) {
    Write-Output "Role assignment completed successfully"
} else {
    Write-Output "Warning: Role assignment may have failed"
}

# ===== SUMMARY =====
Write-Output "`n========== DEPLOYMENT COMPLETED =========="
Write-Output "Resource Group: $env:RG_NAME"
Write-Output "Location: $env:LOCATION"
Write-Output "ACR Name: $env:ACR_NAME"
Write-Output "ACR Login Server: $env:ACR_LOGIN_SERVER"
Write-Output "AI Foundry Account: $env:FOUNDRY_ACCOUNT_NAME"
Write-Output "Project Name: $env:PROJECT_NAME"
Write-Output "Foundry Principal ID: $env:FOUNDRY_PRINCIPAL_ID"
Write-Output "=========================================="


# login in to acr
Write-Output "Logging in to Azure Container Registry: $env:ACR_NAME"
az acr login --name $env:ACR_NAME
Write-Output "Logged in to ACR successfully"

# docker tag and push example image
$localImage = "hostedagent"
$acrImage = "$env:ACR_LOGIN_SERVER/hostedagent:latest"
Write-Output "Tagging local image $localImage as $acrImage"
docker tag $localImage $acrImage
Write-Output "Pushing image to ACR: $acrImage"
docker push $acrImage
Write-Output "Image pushed to ACR successfully"