# Agent course

## Set Up Ollama

- Download Ollama from [ollama.com/download](https://ollama.com/download)
- Pull a model locally:

```powershell
ollama pull qwen2:7b
```

- Start Ollama in the background:

```powershell
ollama serve
```

- To use `LiteLLMModel` instead of `InferenceClientModel`, install the optional dependency:

```powershell
pip install "smolagents[littellm]"
```

```sh
from smolagents import LiteLLMModel

model = LiteLLMModel(
    model_id="ollama_chat/qwen2:7b",  # Or try other Ollama-supported models
    api_base="http://127.0.0.1:11434",  # Default Ollama local server
    num_ctx=8192,
)
```
