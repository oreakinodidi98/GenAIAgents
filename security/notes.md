# Generative AI Security Top Considerations

## Typical GenAI Application Shape

- Initial business app
- Has communication with some sort of external parties
- Called by user/client
- Has a GenAI model that communicates with the app, usually through an orchestrator (LangChain, Semantic Kernel, etc.)
- Dont forget it has to work with the rest of your application
- Things to consider:
  - Private link between Gen AI model and Buisnees APP as we dont want to use public endpoint
  - We dont want to store API key: Entra Authentication or managed identity
  - APIM for input/Output content safety
  - Apply all of the same best practises and governece that drives the rest of your app architecture to keep this secure
- Non determistic
  - Creative and imgaintive in nature
  - Same input will give a slightly different output
  - Security considerations
  - Responsibility considerations
    - need to have constraints to make sure there are no bias or influences
    - easy to social engineer
    - Not very good at keeping sectrets
- Ways to contratrin and controll these behaviours
  - First consideration is the **model** itself
    - make sure it is the right model. Right foundation model
    - people could have backdoored the model or included bias
    - look at who uploaded model in foundry
    - Security in modle tabs -> microsoft has partneredw with hidden layer -> they scan model to make sure no vulnerabilities have been detected
    - Make sure no backdoors
  - Make sure no-one as messed with **dataset**
    - make sure its not been poisoned
    - Make sure dataset is correctly anonymized E.G. Health data
  - **Controll Access** to your own tuned model
    - Restrict API acess to model
    - who has acess to model
    - Model inversion -> work out what model was trained on -> reproduce it to create a copy of model in their own enviroment
    - Bad actor can ectract source material that was used as part of tunning -> Data leaks
  - **Prompt Injection**
    - user can send prompt to application as part of interaction
    - App enriches that propmt by searching the web or grounding
    - **Direct attack** -> jailbreak -> mallicious set of instructions 
      - **DAN** -> Do anything Now
      - **Crescendo** -> part of a multi turn -> been very subtle to trick it to tell us a bit more with each interaction -> do something its not supposed to do
      - **Master Key** -> trying to convince it -> encoding , tricking , bypass the checks it has
    - **In-Direct** -> cross prompt injection attack -> more subtle , trying to sneak in something mallicious
  - **DB**
    - need to lock down data correctly
    - Discover -> Purview
    - classify -> make sure youre not oversharing
    - label
    - Protect
    - to ensure when RAG is ran its not finding classified information
    - make sure applicatio runs interaction in the context of a user
    - Act on behalf of user and user permissions
  - **Plugins**
    - everything i am sending to model can also be sent to plugin
    - if using plugin or agents make sure you really understand and trust them

Need protections aroung GenAI models:

- Content filters
  - violence, hate, sexaual , self harm
- Promp shields for direct and indeirect
- Can protect from responces (infrance from model)
- Test application 
- Pyrit
  - python risk identification tool for Gen AI
  - Red teem -> group of people atacking solution for good intent 
  - Blue team -> people that mitigate and protect application . Red team works with them

Responsibility model

IAAS -> BYOM -> youre responsible for everything
PAAS -> Azure Foundry -> your responsible for APP; plugins; data security
SaaS -> copilot -> responsible for even less

### Model Fundamentals (Context)

- Neural network
- Probability distribution
- Predicts the most likely token
- Fine-tuning of a foundational model
  - Domain-specific focus and expertise
  - Fine-tuning with your own specific dataset to change behavior
  - Normally avoid fine-tuning if data is rapidly changing -> use RAG instead -> but in some cases, fine-tuning is still used

### Key Considerations for GenAI Systems

- Integration
- Observability
- Security
- Governance

## Additional Knowledge and Data Sources

- Also want to add additional knowledge
  - Knowledge from pre-trained sources
  - Vector DB
    - Fantastic for natural language
    - high vectors that represent semantic meaning of data 
    - Vectors that represent semantic query of vector
  - need to lock down data properly
  - Find things based on natural language
  - E.g., Postgres, SharePoint, SQL, Cosmos DB

## External Interactions and Extended Surface Area

- May even interact with the web
- May hook into plugins
  - Copilot
  - SaaS-type GenAI products
- May talk to agents

## Security Framing Note

- As capabilities expand (RAG, plugins, web access, multi-agent communication), the attack surface expands as well.
- This is why integration, observability, security, and governance must be designed together, not treated as separate workstreams.

## Gartner Hype Cycle

- Applies to everything
- Something comes out -> we get a peak of inflated expectations (Care about features) -> then a trough of disillusionment -> then a slope of enlightenment -> then a plateau of productivity (Care about integration with identity, network, security , governence).
- At the plateau, the technology is useful and widely adopted.