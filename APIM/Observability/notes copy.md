# Observability

focus on getting logs and metrics from LLM models
These metrics provide info around user, remaining tokens per user or application, cost about models
charge back for teams (if model is shared by multiple teams)
New policy for emit token metric

App -> APIM (policy for metrics)-> Application insight
can then run queryies using KQL to get more insight and data

To create infrasturcture check IAC
or create APIM
creat foundry
assighn cognitive service to Managed identity
conect to foundy API in APIM
create subscribtion key
make sure log analytic workspace is created
creage application insight 
and connect it to log analytics 
enablle logger in APIM to connect app insights to APIM

## Testing

run python file to send request to foundry through APIM to get some results