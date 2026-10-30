# Foundry

model catalouge -> main powefull feature of service
brings together models unto a new single interface
E.G. GPT-4o, Llama models, Mistral , Microsoft Phi

Choosing right models
capabiloty
cost
laency requirement

benchmarking tools to evaluate models before you commmit
MML view
custom eval
human eval
empty bench 

compare models accross 
accuracy scores
cost per millio token
average latency 
context window size

3 deployment options:
Standard manage compute -> dedicated GPU/CPU
Serveless API -> Model as a service -> per token 
Instant Acess -> call models by name (Protoype/test) -> on demand model acess
All 3 modes respond through the same deployment endpoint

Azure open AI
Enterprise deployment of openAI


Deploy and manage models at production scale

Fine tuning
customise AI models for specific model
using smaller specific dataset
to adjust model for your specific use case

leads to:
consistent tone, style , format
improved accuracy on specialised task
Lower token cost -> shorter prompts neede

When its the right choice:
prompt engineering first point 
RAG -> refrence specific documents
Domain specicf language -> high volume at scale

Prepare training data in json l form
upload to foundry
configure parameters
monitor progress
