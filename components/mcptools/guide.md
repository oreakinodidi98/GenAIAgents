# How to Set Up a Custom MCP Server for Azure AI Agents

This is my working guide for standing up a custom MCP server with Azure Functions. I wanted to keep this practical and close to what I actually did, including the problems I hit and how I worked through them.

## Pre-requisites

- [Azure CLI](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqa1VndUE4ZEd2VURISHRQY2o4N3dWekpQM3BGUXxBQ3Jtc0trU0ZsWHE2UnZ5cEk2N24xUEx4bW5QWlpObUp4cjVsTmJtckZxN1g1ZG9fSTJhbG8xUGdSVlJoU1R4ZEhocUYyZks5Umx0RjFnZVpleElmMXBxUFVqMTdpcXJaeDUzNzYzYXhTZlVwc1IwWkdiUl9mSQ&q=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fcli%2Fazure%2Finstall-azure-cli%3Fview%3Dazure-cli-latest&v=cDGBGHXal9M)
- [Azure Function Core tools](https://github.com/Azure/azure-functions-core-tools?tab=readme-ov-file#installing-the-cli)
- [Python](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbGxXR2F5UG5UOTVHQlFCQTQ2Nlc3LVIyek1EZ3xBQ3Jtc0trc1l4Qy1lcDBuZk1QcHNPV2JWSnlHYXpsd1pJVGFmV1N2bjY5R0pWWVRGUm5YWEFRUEtsdXRpQzk4LTlPNkdzVWNzcHBjT08weS00dDdRdEV5ZmV4cHlBR3pQaTFJb05IUjRBUTU0M0pQOExKaVg1OA&q=https%3A%2F%2Fwww.python.org%2Fdownloads%2F&v=cDGBGHXal9M)
- [Node.js](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbEVGX0dfUkpRRWV4aG03dm1QSjJZc19LcU1aQXxBQ3Jtc0tsOFNNVU9aWGpqOEVSa2VZWnM4MzBnOFBwUWdhTkFtRkI3ajR1ZHloZTB3cWNsQ2hyUmNzSFZGZnBNcVJSdWhqc1g0ZUNCTFUxLW1KVWpIcmpjS3Z2cW5FTEgtbnBGSm9Qd1hKYk5JMk5uNFVSc0NRSQ&q=https%3A%2F%2Fnodejs.org%2Fen&v=cDGBGHXal9M)

## What This Creates

The goal is to create a Python Azure Function project that exposes an MCP tool and can later be connected from a client through an MCP HTTP endpoint.

Expected files after scaffolding:

- `requirements.txt`
- `local.settings.json`
- `host.json`
- `function_app.py`

## Steps

### 1. Create the Function project

1. Go to VS Code.
2. Create a new Function project either using the extension or `func new`.
3. Choose:
   - Python
   - MCP trigger
   - Default name
   - Function authorization level

That should produce the requirements file, local settings file, host file, and the function app code for the tools.

### 2. Create and activate the virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Update the Functions Python package

Use the latest preview package that supports the MCP decorator pattern:

```txt
azure-functions==1.25.0b3
```

### 5. Update local settings

Add this value in local settings:

```json
"PYTHON_ISOLATE_WORKER_DEPENDENCIES": "1"
```

### 6. Simplify the decorator

Use the simpler decorator style in the function app:

```python
@app.mcp_tool()
def mcp_trigger(context):
    return "Hello I am MCPTool!"
```

### 7. Start the local MCP server

```powershell
func start
```

If everything is wired correctly, you should see the endpoint and the list of tools.

### 8. Test from VS Code

1. Go to the `.vscode` folder.
2. Create an `mcp.json` file.
3. Add the server.
4. Use HTTP and add the endpoint.
5. Give it a name.
6. Will list tools and we can start.
7. Test in copilot chat to trigger MCP tool trigger from local MCP server.

### Test in MCP inspector

1. pe terminal
2. npx @modelcontextprotocol/inspector
3. set streamable Add endpoint as url
4. connect

## Push to cloud in azure functions and use as remote MCP server

## Storage Setup for Azure Functions

To fully run this, the Functions host still needs `AzureWebJobsStorage`.

There are two practical ways to do that:

- Connect to a local storage emulator.
- Connect to a real Azure Storage account.

I ended up testing the real Azure Storage account path as well as the local emulator path.

### Option 1. Local storage emulator

You can connect to a local storage emulator like Azurite.

Important note: Azurite is a Node.js package, not a Python package.

Install it with:

```powershell
npm install -g azurite
```

Then run it in another terminal:

```powershell
azurite -s
```

### Option 2. Azure Storage account with shared key auth

If local auth is allowed on the storage account, you can use a normal connection string in `AzureWebJobsStorage`.

If shared key access is disabled and policy allows you to turn it back on, one option is:

```powershell
Get-AzStorageAccount | Where-Object { $_.AllowSharedKeyAccess -eq $false } | ForEach-Object {
  Set-AzStorageAccount -ResourceGroupName $_.ResourceGroupName -Name $_.StorageAccountName -AllowSharedKeyAccess $true
}
```

Or with Azure CLI:

```powershell
az storage account update --name <storage-account-name> --resource-group <resource-group> --allow-shared-key-access true
```

In my case, the CLI command returned successfully but the storage account still showed:

```json
"allowSharedKeyAccess": false
```

So the likely cause there is policy or permission enforcement at a higher scope.

### Option 3. Azure Storage account with identity-based connection

This ended up being the better path for the setup I was working on.

For local development, use the documented identity-based format for `AzureWebJobsStorage` in `local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage__blobServiceUri": "https://oaaidemo.blob.core.windows.net",
    "AzureWebJobsStorage__queueServiceUri": "https://oaaidemo.queue.core.windows.net",
    "AzureWebJobsStorage__tableServiceUri": "https://oaaidemo.table.core.windows.net",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "PYTHON_ISOLATE_WORKER_DEPENDENCIES": "1"
  }
}
```

Important note:

- For local development, do not use a blob-only SAS string for `AzureWebJobsStorage`.
- The Functions host needs more than blob access.
- In my case, a blob-only setting caused `AuthorizationFailure` and health-check issues.
- Also, I removed `AzureWebJobsStorage__credential=azurecli` after validating the documented guidance. Local development uses the signed-in developer identity automatically.

## Azure Auth Commands I Used

### If using Azure PowerShell

PowerShell Az commands and Azure CLI login do not share the same auth context automatically.

If you are using `Get-AzStorageAccount` or `Set-AzStorageAccount`, first do:

```powershell
Connect-AzAccount
Get-AzSubscription
Set-AzContext -SubscriptionId "<subscription-id>"
```

### If using Azure CLI

If you are already signed in with Azure CLI, you can use:

```powershell
az login
az account show
```

I found using Azure CLI simpler when I was already logged in there.

## RBAC for Identity-Based Storage Access

If using managed identity / developer identity access to the storage account, first get your signed-in user object ID:

```powershell
$userId = az ad signed-in-user show --query id -o tsv
```

Then define the storage scope:

```powershell
$scope = "/subscriptions/cb5b077c-3ef5-4b2e-83e5-490cc5ca0e19/resourceGroups/AI_Demo/providers/Microsoft.Storage/storageAccounts/oaaidemo"
```

Then assign the needed roles.

At minimum, these were part of the troubleshooting flow:

```powershell
az role assignment create --assignee $userId --role "Storage Blob Data Contributor" --scope $scope
az role assignment create --assignee $userId --role "Storage Queue Data Contributor" --scope $scope
az role assignment create --assignee $userId --role "Storage Table Data Contributor" --scope $scope
```

Best-practice note:

- For Azure Functions host storage, the Microsoft guidance calls out `Storage Blob Data Owner` as the minimum host-storage role for normal operation.
- `Storage Table Data Contributor` is also useful for diagnostic events.
- If blob contributor is not enough in your environment, upgrade that role assignment to `Storage Blob Data Owner`.

## Troubleshooting

This is the part that mattered most in practice.

### 1. `KeyBasedAuthenticationNotPermitted`

If you see:

```text
Unable to access AzureWebJobsStorage
errorCode: KeyBasedAuthenticationNotPermitted
```

That means the Functions host is trying to use a storage account key, but the storage account does not allow key-based auth.

Ways around it:

- Re-enable shared key access if policy allows.
- Use Azurite locally.
- Use an identity-based `AzureWebJobsStorage` configuration.

### 2. `AuthorizationFailure`

If you see:

```text
Unable to access AzureWebJobsStorage
errorCode: AuthorizationFailure
```

That usually means one of these:

- The storage settings are incomplete.
- You used only blob access and left out queue/table endpoints.
- Your identity does not have the right data-plane roles.
- RBAC changes have not propagated yet.

What fixed it for me:

- Use `AzureWebJobsStorage__blobServiceUri`
- Use `AzureWebJobsStorage__queueServiceUri`
- Use `AzureWebJobsStorage__tableServiceUri`
- Assign queue and table roles in addition to blob access
- Start the Functions host again with verbose logs

```powershell
func start --verbose
```

### 3. Azure CLI vs PowerShell confusion

I hit this one too.

If `az login` worked, but PowerShell still says:

```text
No subscription found in the context.
```

That means you authenticated with Azure CLI, but not with PowerShell Az.

Use either:

```powershell
Connect-AzAccount
```

or just stay fully in Azure CLI commands for that part.

### 4. Azurite install issue

If you try:

```powershell
pip install azurite
```

and get:

```text
No matching distribution found for azurite
```

that is expected. Azurite is not a Python package.

Use:

```powershell
npm install -g azurite
```

### 5. Storage auth was fixed, then MCP binding was fixed

After switching `AzureWebJobsStorage` to the identity-based URI configuration, storage startup errors were resolved.

The next issue was:

```text
The 'dispatch_vbd' function is in error: The binding type(s) 'mcpToolTrigger' were not found in the configured extension bundle.
```

That was resolved by:

1. Setting `host.json` extension bundle version to `"[4.22.0, 5.0.0)"`.
2. Clearing local extension bundle cache:

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.azure-functions-core-tools\Functions\ExtensionBundles\Microsoft.Azure.Functions.ExtensionBundle" -ErrorAction SilentlyContinue
```

3. Restarting Functions host.

After that, MCP tools registered correctly as `mcpToolTrigger`.

### 6. Repeating `NoScriptHost` health warnings after MCP tools are listed

You may still see periodic health warnings like:

```text
azure.functions.script_host.lifecycle: Unhealthy
description: No script host available
errorCode: NoScriptHost
```

If all MCP tools are listed and endpoints are printed, this can be a preview/runtime health-check mismatch rather than a real outage.

Treat this as non-blocking when all of the following are true:

1. Startup prints MCP endpoints.
2. Functions list includes your MCP tools.
3. Storage health remains `Healthy`.

### 7. About the Foundry local-auth command

For Foundry / Cognitive Services local auth, this PowerShell command re-enables local auth for Cognitive Services accounts where it was disabled:

```powershell
Get-AzCognitiveServicesAccount | Where-Object { $_.DisableLocalAuth -eq $true -and $_.AccountName -and $_.ResourceGroupName -and $_.Id } | ForEach-Object { Update-AzTag -ResourceId $_.Id -Tag @{SecurityControl='Ignore'} -Operation Merge | Out-Null; Set-AzCognitiveServicesAccount -ResourceGroupName $_.ResourceGroupName -Name $_.AccountName -DisableLocalAuth $false | Out-Null }
```

This does not fix Azure Storage host auth directly, but it is still useful when working with Foundry-related services that have local auth turned off.

## Practical Summary

The cleanest order I would follow now is:

1. Create the Function project.
2. Create and activate `.venv`.
3. Install requirements.
4. Set `azure-functions==1.25.0b3`.
5. Add `PYTHON_ISOLATE_WORKER_DEPENDENCIES=1`.
6. Use `@app.mcp_tool()`.
7. Configure `AzureWebJobsStorage` using identity-based service URIs if shared key access is blocked.
8. Assign the needed RBAC roles on the storage account.
9. Run `func start --verbose`.
10. If `mcpToolTrigger` fails, pin extension bundle to `"[4.22.0, 5.0.0)"`, clear bundle cache, and restart.
11. If periodic `NoScriptHost` health warnings appear but MCP tools are listed and endpoints are live, treat it as non-blocking preview telemetry noise.
12. Create function APP.
    1. Flex consumption.
    2. Connect to existing storage account.
13. Publish local funcrion to function APP (Remote MCP server).
    1. Func azure functionapp publish <name of function app>
    2. Test in VS code.
        1. Get url.
        2. Add server -> http -> add https///<name>//runtime/webhooks/mcp/
        3. use following format """,

```json
{
  "my-mcp-remote-server": {
    "url": "https://<YourFunctionAApp>.azurewebsites.net/runtime/webhooks/mcp",
    "type": "http",
    "headers": {
      "x-functions-key": "<YourMCPKey>"
    }
  }
}
```

        4. get app keys from function
        5. Start
        6. Open up github chat window and select MCP server
    3. Test in MCP inspector: npx @modelcontextprotocol/inspector
        1. function key as authentication
14. Connect to Azure AI Agent in Foundry.
    1. Add new Tool.
    2. custom tools -> MCP.
    3. create custom endpoint.
    4. add Azure function url as endppoint.
    5. from "https://<YourFunctionAApp>.azurewebsites.net/runtime/webhooks/mcp"
    6. chose authentication method.
    7. save test.
    8. Can configure with specific allow tools or approval settings

That last point matters. It is easy to think storage or startup is still broken when MCP is actually running and only readiness telemetry is noisy.
