# Deploy LLM in Container Apps using Serverless GPU

serveless GPU -> GPU powered workload profiles
to see whats avaialbe in region run : az containerapp env workload-profile list-supported -l swedencentral -o table

the   Consumption-GPU-NC8as-T4 is a smaller more affordable option for SLM Consumption-GPU-NC24-A100 Nvidia A100 for LLM (1 billion parameters)

its serveles
app can sclae down to 0 
billed per second
so only pay while GPU is working

to serve model use Vllm -> open source infrence server used for production
desighned for many concurent users at high througput 
using pagedattention managing GPU memory an OS manages RAM
Continous batching -> keeps GPU busy at all times
scales
runs on any hardwaare

official docker deployment for [vLLM](https://docs.vllm.ai/en/latest/deployment/docker/)

docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HF_TOKEN=$HF_TOKEN" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen3-0.6B

docker run -itb --name gemma4 --network host --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --shm-size 16G \
    --ipc=host \
    vllm/vllm-openai:gemma4-cu130 \
    --model google/gemma-4-31B-it --tensor-parallel-size 2 --max-model-len 32768 \
    --gpu-memory-utilization 0.90 --host 0.0.0.0 --port 8000

in azure type nvidia-smi to configure

catch/disadvantages:
model is huge
Loading all into GPU memory takes time
this appens every time because you scale to 0 -> cold start

buttleneck is loading the model into GPU memory -> might use a storage account file shareto cut repeated downtime

can monitor model -> gpu metrics for container apps out of the box

## cost

serveles GPU are billed per second
only pay for the resources you allocate so cheaper than VM and AKS
ACA -> GPU -> Vllm (infrencing)-> Model

## Demo: deploy model into ACA

run terraform folder to run resources
creates rg
container apps enviroment
consumption group profile 
profile of D4 and GPU for contianer apps
uses az comand line to provision th resources and workload profile doesnt work in terraform at the moment
deploy ACA that will run gemma 4 -> expose on port 1800 -> using VLLM continer, specify resource limits, configured http scale rule based of KEDA