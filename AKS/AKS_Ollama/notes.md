---
title: Running LLMs on AKS with Ollama
description: Notes on running and consuming language models locally, in containers, and on AKS
---

## Why run an LLM on AKS

Running a large language model (LLM) on your own infrastructure gives you more
control over the model and the data sent to it. This is useful when a customer
needs the model to remain within their own infrastructure and network.

An LLM needs a platform to host and serve it. This demo focuses on Ollama, which
can run different model families on a CPU or GPU. Other platforms include
Hugging Face, NVIDIA, and LM Studio.

## Get started with Ollama

Install Ollama on your machine, then download and run a model:

```powershell
ollama run <model-name>
```

You can chat with the model directly from the terminal. Most companies and
users, however, will use a client or chat application to interact with it.

Ollama exposes its models through a REST API. A client application can send
chat requests to the `/api/chat` endpoint, while applications such as Open
WebUI provide a browser-based chat experience. The same Ollama instance can
serve multiple supported models.

## Demo

1. Run Ollama on the local machine.
2. Run Ollama in a Docker container.
3. Deploy Ollama to an AKS cluster.
4. Connect Open WebUI to Ollama and interact with the model.

### Run Ollama locally

[Download and install Ollama](https://github.com/ollama/ollama), then run a
model from the command line:

```powershell
ollama run phi3.5
```

You can now interact with the model directly in the terminal. End users will
usually interact with it through a client application instead. Ollama supports
this by exposing the model through a REST API on port `11434`.

The following PowerShell example sends a message to the chat endpoint:

```powershell
$body = @{
    model = "phi3.5"
    messages = @(
        @{ role = "user"; content = "Who are you?" }
    )
} | ConvertTo-Json -Depth 3

Invoke-RestMethod `
    -Uri "http://localhost:11434/api/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### Run Ollama and Open WebUI in Docker

The [Ollama Docker image](https://hub.docker.com/r/ollama/ollama) provides the
same API from a container. Run Ollama with a named volume so downloaded models
remain available when the container restarts:

```powershell
docker run -d `
    -v ollama:/root/.ollama `
    -p 11434:11434 `
    --name ollama `
    ollama/ollama
```

Check for active models, then download and run `phi3.5` inside the container:

```powershell
docker exec -it ollama ollama ps
docker exec -it ollama ollama run phi3.5
```

[Open WebUI](https://github.com/open-webui/open-webui) provides a browser-based
interface for interacting with Ollama. Run it on port `3001` and configure it
to connect to Ollama through the host:

```powershell
docker run -d `
    -p 3001:8080 `
    --add-host=host.docker.internal:host-gateway `
    -v open-webui:/app/backend/data `
    -e WEBUI_AUTH=False `
    -e OLLAMA_BASE_URL=http://host.docker.internal:11434 `
    --name open-webui `
    --restart always `
    ghcr.io/open-webui/open-webui:main
```

This command disables authentication for the local demo and uses a named
volume to persist the Open WebUI data. Check that both containers are running:

```powershell
docker ps
```

Open <http://localhost:3001> in a browser. You can use the interface to chat
with `phi3.5` or download and select another supported model.

### Deploy Ollama and Open WebUI to AKS

The Kubernetes manifests in the `k8s` directory move the same setup to AKS:

* The Ollama StatefulSet runs one replica of the latest Ollama container.
* CPU and memory requests and limits are defined, but no GPU is requested.
* A volume claim template creates persistent storage for downloaded models.
* The Ollama Service exposes port `11434` inside the cluster.
* The Open WebUI Deployment connects to Ollama through the service URL stored
  in the `OLLAMA_BASE_URL` environment variable.
* A separate persistent volume claim stores the Open WebUI application data.
* The Open WebUI Service exposes the application inside the cluster.
* The optional Ingress makes Open WebUI available outside the cluster when an
  ingress controller is installed.

Apply the manifests from the `AKS_Ollama` directory:

```powershell
kubectl apply -f .\k8s
```

#### Download a model

The Ollama container starts without a model. Download `phi3.5` into the
persistent Ollama volume:

```powershell
kubectl exec -n ollama ollama-0 -- ollama pull phi3.5
```

You can replace `phi3.5` with another supported model, such as `llama3.1`.
Confirm that the model is available:

```powershell
kubectl exec -n ollama ollama-0 -- ollama list
```

To test the model in an interactive terminal session, run:

```powershell
kubectl exec -n ollama -it ollama-0 -- ollama run phi3.5
```

Press `Ctrl+D` to leave the session. The downloaded model remains on the
persistent volume after the pod or cluster restarts.

#### Open the web interface

Check the Open WebUI service and note its `EXTERNAL-IP` value:

```powershell
kubectl get service -n ollama open-webui-service
```

Open `http://<EXTERNAL-IP>` in a browser. The service accepts traffic on port
`80` and forwards it to Open WebUI on port `8080`.

> [!IMPORTANT]
> Restrict public access with an NSG or firewall rule. Allow only trusted
> source IP addresses, preferably the current client public IP with a `/32`
> prefix, instead of exposing Open WebUI to the entire internet.

### Troubleshoot the AKS deployment

#### The browser connection times out

Confirm that the AKS cluster and node pool are running:

```powershell
$resourceGroup = "<resource-group>"
$clusterName = "<cluster-name>"

az aks show `
    --resource-group $resourceGroup `
    --name $clusterName `
    --query "{powerState:powerState.code,provisioningState:provisioningState}"

az aks nodepool list `
    --resource-group $resourceGroup `
    --cluster-name $clusterName `
    --query "[].{name:name, power:powerState.code, state:provisioningState}" `
    --output table
```

If the cluster is stopped, start it and wait for provisioning to finish:

```powershell
az aks start --resource-group $resourceGroup --name $clusterName
az aks wait `
    --resource-group $resourceGroup `
    --name $clusterName `
    --updated `
    --interval 30 `
    --timeout 1800
```

Refresh the Kubernetes credentials, then check the nodes:

```powershell
az aks get-credentials `
    --resource-group $resourceGroup `
    --name $clusterName `
    --overwrite-existing

kubectl get nodes
```

All nodes should report `Ready` before you test Open WebUI again.

#### A pod is not running

Check the pod status and recent cluster events:

```powershell
kubectl get pods -n ollama -o wide
kubectl get events -n ollama --sort-by=.lastTimestamp
```

Use the pod name from the first command to inspect scheduling, image, or volume
errors:

```powershell
kubectl describe pod -n ollama <pod-name>
kubectl logs -n ollama <pod-name>
```

If a pod is temporarily in `ContainerCreating` after the cluster starts, wait
for its persistent volume to attach and its image to download.

#### The external IP is pending or unavailable

Inspect the service and verify that it has a healthy backend endpoint:

```powershell
kubectl get service -n ollama open-webui-service -o wide
kubectl get endpointslice -n ollama `
    -l kubernetes.io/service-name=open-webui-service
```

An `EXTERNAL-IP` value of `<pending>` means the Azure Load Balancer is still
being created. If an IP exists but no endpoint is listed, confirm that the
Open WebUI pod is `Running` and `Ready`.

#### Open WebUI cannot find a model

Confirm that Ollama is running and that the model was downloaded:

```powershell
kubectl get pod -n ollama ollama-0
kubectl exec -n ollama ollama-0 -- ollama list
kubectl logs -n ollama ollama-0
```

If the model is missing, run the `ollama pull` command again. If Open WebUI
still cannot connect, verify that the Ollama service has an endpoint:

```powershell
kubectl get service -n ollama ollama-service
kubectl get endpointslice -n ollama `
    -l kubernetes.io/service-name=ollama-service
```

#### Persistent storage does not attach

Check that both claims are bound:

```powershell
kubectl get persistentvolumeclaim -n ollama
```

The `ollama-volume-ollama-0` and `open-webui-pvc` claims should report
`Bound`. Use `kubectl describe persistentvolumeclaim -n ollama <claim-name>`
to inspect a claim that remains `Pending`.
