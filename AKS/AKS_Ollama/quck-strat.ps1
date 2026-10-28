
# Generate a random number
$RAND = Get-Random

# Set it as an environment variable
$env:RAND = $RAND

# Print the random resource identifier
Write-Output "Random resource identifier will be: $RAND"
# Parameters
$env:LOCATION = 'swedencentral'
$env:AKS_RG="rg-aks-dev-ollama-$RAND"
$env:AKS_NAME="aks-dev-ollama-$RAND"
$env:AKS_NODE_VM="Standard_D2s_v5"

# create resource group
az group create -n $env:AKS_RG -l $env:LOCATION
# create an AKS cluster 
az aks create -n $env:AKS_NAME -g $env:AKS_RG --network-plugin azure --network-plugin-mode overlay -k 1.30.3 --node-vm-size $env:AKS_NODE_VM
# get credentials
az aks get-credentials -n $env:AKS_NAME -g $env:AKS_RG --overwrite-existing
# check AKS Sconnection
kubectl get nodes
# deploy Ollama server and client app (Open-WebUI) into AKS
kubectl apply -f /c:/GenAI/Agents/AKS_OLLAMA/k8s .
# check the install
kubectl get all,pv,pvc -n ollama

# install LLM model likw phi3.5 or llama3.1 into ollama server
kubectl exec ollama-0 -n ollama -it -- ollama run phi3.5

# or you can run another model like llama3.1
kubectl exec ollama-0 -n ollama -it -- ollama run llama3.1

# get the public IP of the client service
kubectl get svc -n ollama