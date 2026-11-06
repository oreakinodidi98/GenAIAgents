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

## Policy error handling

The three API policies route to `Backendpool`. Backend membership, weights,
priorities, and circuit breakers are configured on the backend resources, not
in these policies.

`foundry-service-api-ai.xml` preserves backend HTTP error statuses and wraps the
backend error body in diagnostic JSON. Missing or invalid APIM subscription keys
are mapped to HTTP 401 when handled by its `on-error` section.

The France and UK policies check that a response exists before inspecting its
status in `on-error`. Their token limits, metrics, and retry settings remain
specific to each API entry point; selecting a pool member does not execute
another API's policies.

After applying the policies in APIM, test a successful request, missing and
invalid subscription keys, an invalid model, backend throttling, and backend
unavailability. Use request traces to confirm the selected pool member. Backend
400 and 429 responses should retain their status through the diagnostic policy;
missing and invalid subscription keys should return 401.

## testing 

Create APIM and 3 instances of Foundry
deploy model on each foundry
connect in apim
set up backend 

create a venv and run it 
```powershell
python -m venv agent_env
.\agent_env\Scripts\Activate.ps1
```

Install the project's packages:

```powershell
python -m pip install -r requirements.txt
```