---
title: Azure API Management and Azure OpenAI
description: Load Balancing
---

## APIM

Load balancing to send request to multiple llm models withing APIM
important because of llm model constraints
main limitation: input token
but want the app to be alwasy available

solutions:
increase limits
pay as you go through PTU
Global and data zone deployment
Multiple instances of LLM models

## Multiple instances of LLM models

can create Multiple instances of LLM models in different regions
in APIM can configure to 
spread the load to multpile backends which may have individual backend circuit breakers
shift the load from one set of backends to another for upgrade (blue green deployments)
round robin load balancing
doesn need policy configuration
rules are properties of backend
supports weiht and priority of each instance 

## testing 

create a venv and run it 
```powershell
python -m venv agent_env
.\agent_env\Scripts\Activate.ps1
```

Install the project's packages:

```powershell
python -m pip install -r requirements.txt
```