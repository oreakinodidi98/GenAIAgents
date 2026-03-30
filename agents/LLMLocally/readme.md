# LLM Locally

using foundary [local](https://www.foundrylocal.ai/)

## Why run LLM locally

- keep data private
- Save money in terms of token cost
- Open source models
- Can't run propriatery Models like GPT
- Downloads to machine

### instructions

1. winget install Microsoft.FoundryLocal
2. foundry model run qwen2.5-0.5b

## commands

- ```foundry --help```
- ```foundry service status```
- ```uv init foundry-local-demo```
- ```uv venv```
- ``` .\.venv\Scripts\Activate.ps1 ```
- ```uv add openai```
- ```uv add foundry-local-sdk```
- ```uv add langchain_openai```
- ```uv add langchain_community```
- ```uv add pypdf```

## code

1. create alias -> alias = qwen2.5-0.5b
2. import FoundryLocalManager; openai
3. Create manager with alias