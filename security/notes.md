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

## Secure AI Agents: A Practical Overview for Development Teams

The focus here is making sure the tools your agents use are secure and enterprise-ready.

The current reality is that AI agents are moving into production faster than the security practices around them are maturing. Even in organisations with strong security awareness, agents behave fundamentally differently from the applications security teams are used to protecting. An agent decides for itself which tools to call, what data to pass between them, and how to chain actions together across multiple steps. Traditional controls built around static API endpoints and predefined workflows were not designed for that level of autonomy.

This is why we need security beyond permission prompts. Prompts that ask a human to approve every action slow the agent down and eventually train people to click "allow" reflexively. Securing AI agents is not about slowing them down. It is about building the infrastructure that lets them operate with full autonomy inside boundaries that contain risk. The agents themselves are only as dangerous as the environments they run in and the access they are granted.

Below are the key security domains I would focus on when deploying AI agents:

- Execution isolation and network boundaries
- Agent access and tool governance
- Identity and credential management
- Observability, evaluation, and multi-agent trust

### Agent vs. web service

A web service usually follows a predictable model: requests come in through defined endpoints, deterministic logic processes them, and structured responses come back out. We design controls around that predictability because we know the shape of the interaction before it happens.

Agents are different. They interpret instructions dynamically, select tools at runtime, and chain multiple operations together without human approval at each step. A coding agent might read a file, install a dependency, modify configuration, run tests, and push a commit, all from a single prompt. A data agent might query three APIs, correlate the results, and write a summary to a shared document.

That extra autonomy is what makes agents powerful, but it is also what expands the attack surface. A compromised or misdirected agent can take a much wider range of actions than a compromised traditional service. And because agents often run with the credentials and permissions of the developer or system that launched them, one security failure can cascade across every system the agent can reach.

## Execution Isolation

If an agent operates directly on your host machine, everything on that machine is within its reach: file systems, network interfaces, credentials stored in environment variables, and running services. Any vulnerability in the agent's logic, or any successful prompt injection, now has a path into your full development environment.

From a practical standpoint, this is one of the highest-impact controls you can put in place. It limits blast radius, and it usually does so with less friction than people expect.

### Sandboxed environment

The first step is to run each agent in its own isolated, disposable environment. That could be a microVM, a hardened container, or a dedicated sandbox. The goal is to give the agent a real working environment where it can install packages, run services, and modify files, while making sure it cannot reach the host machine or other agents directly.

If something goes wrong, you destroy the environment and spin up a new one. That gives your agents full autonomy inside a boundary, which is both faster and more secure.

### Networking

Isolation is not just about the file system or process boundary. It is also about network control.

- Restrict network access to only the endpoints the agent actually needs.
- Allow list specific domains and APIs.
- Block egress traffic to unknown destinations.
- Be deliberate about where the agent is allowed to run from and what it is allowed to talk to.

## Agent Access

The next concern is controlling what the agent can do. Agents interact with external systems through tools, API connectors, database queries, file operations, and code execution environments. Every one of those is an access point.

From a security standpoint, the question is not just whether a tool is useful. The question is whether that tool should be available for this specific task, in this specific environment, for this specific role. That is where just-in-time access becomes important. Instead of pre-loading every tool the agent might ever need, you grant access only when it is required.

This can be enforced through a gateway or control plane that applies policy across agents and sessions, filtering which tools are available based on task, environment, and role.

### Tools and skills

Another attack area is tool or skill poisoning. This is where a malicious tool description, skill definition, or configuration manipulates the agent into performing unintended actions. Because agents are designed to follow tool and skill descriptions, they do not automatically know the difference between legitimate instructions and injected ones.

This is very similar to a traditional supply chain attack. Instead of compromising a package dependency, the attacker compromises the instructions or metadata the agent relies on to decide what to do next.

To reduce that risk:

- Use validated model and tool registries.
- Review markdown configurations and skill definitions before using them.
- Monitor for behaviour that falls outside what that tool or skill is expected to do.
- Route tool calls through a centralised gateway so policy enforcement is consistent.

## Identity Management

This is very similar to how we think about workload identities in the rest of cloud security: least privilege still applies, and we should not be sharing the credentials of the developer who launched the agent.

When an agent runs under your personal access token, every action it takes inherits your full permissions. If the agent is compromised, the attacker inherits those permissions too. Instead, agents should be provisioned with dedicated, scoped credentials that carry only the permissions the task requires.

In other words, agents need to be treated as first-class identities in your access management system, the same way you would treat service accounts.

### Credential management

The credential handling pattern is also very similar to traditional applications:

- Store credentials in secret management tools.
- Inject them into the agent environment at runtime.
- Rotate them automatically.
- Make sure secrets are not persisted in agent memory, logs, or conversation context where they could later be extracted through prompt injection.

## Observability

An agent that runs autonomously with no visibility into its actions is a liability. At some point you will need to answer the question: what exactly did this agent do, and why? That could be for incident response, a compliance review, or just understanding why the agent produced an unexpected result.

Traditional application logging mainly captures requests and responses. Agent logging needs to capture the decision chain as well. You want to see which tools were called, in what order, with what parameters, and what the agent decided to do with the results.

This needs to be designed in from the start, not retrofitted later.

### Model eval and baselining

Agents can behave differently over time as models update, prompts evolve, or context changes.

- A coding agent that reliably used three tools last week might start invoking a fourth after a model update.
- A data pipeline agent might begin accessing tables outside its normal scope because a prompt template changed upstream.

This is why organisations need to establish baselines. What does normal look like for each agent in terms of tool calls, frequency, and parameter patterns? Once you have that baseline, you can flag deviations.

Signals worth investigating include:

- First-time tool invocations
- Access to resources outside the agent's historical scope
- Outputs that differ significantly from prior runs

### Agent-to-agent trust

As soon as you move into multi-agent orchestration, you also need to think about trust between agents.

If agent A hands a payload to agent B, and agent B acts on it without validation, a compromise in one agent can propagate through the chain. That means inter-agent communication should be treated as untrusted input. Each agent's permissions should be scoped independently, and delegation should never silently escalate privileges.

If an orchestrator agent can spin up a coding agent, that coding agent should not automatically inherit the orchestrator's full toolset or credentials. Those boundaries become essential once you move from a single agent to a coordinated fleet.
