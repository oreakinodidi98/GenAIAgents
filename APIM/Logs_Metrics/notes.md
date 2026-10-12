# Collecting logs and Metrics from APIM

## Why

usefull in helping gather accurate cross charging based on token consumption
charge back: when the model is shared beween multiple teams/applications can then charge the correct team
collect token usage data

flow:
Request -> API (Metrics) -> foundry -> App insinght

by default they have metrics and logs to get use of API
but for OpenAI they have a custom policy to collect this in APIM

can collect subID, Client IP and APIID

can use KQL to create and gather: 
custom metrics
Requests -> get logs for all requests been served ( gives full plomt , system prompt, compreltion, user questio, number of tokens consumed)
can visualise in graffan dashboards

## Demo

Resources:
Resource group
Apim: consumption plan, 2 RBAC roles (cognitive user, Monitoring), importing API file for Model using swager but can connect directly in inentory, enable subsribtion
Foundry: For LLM models with model deployment, globalstandard
App insights: to enable diagnostics, Log analytics workspace
Grafana