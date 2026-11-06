---
title: Azure API Management and Azure OpenAI
description: 
---

## APIM

APIM is not just the front door to APIs — it can be the security, governance, observability and traffic-management layer for an enterprise API platform. You would tpically use APIM to make it easier to manage your backend API, E.G. Load balancing, Authentication (APIM subscribtion key on application -> APIM with Managed identity and RBAC -> Backend API), Cache (caching User request and responce), tracing for metrics and logs, mock API (before implementing real API), Logs/Metrics in Azzure monitor. All of these features can be defined through a policy applied in APIM for each API. These work well for a backend API that is a rest API but can also be used for LLM model like OpenAI, Minstral etc. Can still apply the following for these models. Allowing you to take advantage of priority retry , circuit breaker patterns in the load balancer or LLM token limits and LLM metrics policy to help overcome constraints for LLM models around token limits for models and regions.

Essentially APIM Acts as the governed boundary with policy‑as‑code that keeps agent tools secure and scalable.

Security — Entra ID, OAuth 2.0, JWT validation & policies
Traffic Management — Rate limiting, throttling & routing
Hybrid Connectivity — Secure access to Azure and on-prem APIs
Observability — Azure Monitor, Application Insights & centralized logging
Governance — API versioning, lifecycle management & access control
Resiliency — HA, DR and multi-region considerations
Automation — Terraform/Bicep and CI/CD for consistent deployments
Semantic caching - Connecting to redis cache that saves user prompt and responce from LLM model. Using embeding model , transfering user prompt to a vector and searching for the nearest vestor stored in redis cache
Streaming - Chunks of the responce

Why it matters:
✅ Stronger governance: keep APIs consistent, controlled, and enterprise-ready
✅ Better security posture: centralized policies, authentication, and traffic control 🛡️
✅ Faster delivery: streamline how teams publish and manage APIs across workloads
✅ Smoother integration: connect services with clearer boundaries and fewer surprises 🔗

## Create an Azure API Management instance

Before deploying any Azure resources, its important to first define a consistent naming convention. For this blog, I use the application name, environment, region, instance number, and owner to build each resource name.

| Component        | Value | Meaning              |
|------------------|-------|----------------------|
| Application name | `hol` | Hands-on lab         |
| Environment      | `dev` | Development          |
| Region           | `sc`  | Sweden Central       |
| Instance         | `01`  | First instance       |
| Owner            | `oa`  | Resource owner       |

I use the following naming patterns:

* Resource group: `rg-<environment>-<region>-<application-name>-<owner>-<instance>`
* API Management: `apim-<environment>-<region>-<application-name>-<owner>-<instance>`

The API Management service name must be globally unique. Including the owner value helps you create a unique name and identify who owns the resource.

You should also make a note of the API Management service name because you will use it to build URLs later in the lab.

For this exercise, we will select the **Developer** tier because it provides the features needed at the lowest cost.

![APIM Service Creation](..\APIM\Cost\images\image.png)

## Verify the Azure API Management instance

The deployment can take some time because Azure creates several supporting resources in the background. Once the deployment is complete verify that your API Management instance is working:

1. In the Azure portal, open the new API Management instance.
2. Select **APIs**, and then select **Echo API**.
3. On the **Test** tab, select the **GET Retrieve resource** operation.
4. Select **Send** to issue a test request.
5. Confirm that the response has a `200 Success` status.

> [!IMPORTANT]
> When you open the request URL in a browser or call it with CURL, you initially receive a `401 Unauthorized` response. The Echo API requires a subscription key by default. Tests sent from the API Management test console include this key automatically, but external requests do not.

For this lab, temporarily disabled this requirement so you can test the API from
outside the Azure portal. In **Echo API**, open the **Settings** tab, clear **Subscription required**, and select **Save**.

Subscriptions are valuable for controlling and monitoring API access. Disable this setting only to confirm that the API Management instance works as expected in this lab.

You can now open the request URL in my browser or run the following verbose CURL
command. The request should return a `200 Success` response:

```bash
curl -v "https://<apim-instance-name>.azure-api.net/echo/resource?param1=sample"
```

## GenAI Gateway

APIM adds to the security, resilliency and scalability of customers backend API
With the inrodction of AI services , LLM models (OpenAI, LLama, Mistral) they have their own constraints 
Mostly related to Tokens
Gen AI gateway is a solution for these constraints . These are APIM new capabilities and new policies
This makes it easier to work with LLM models by adding support for policies that will make it easier to get things like 

- Usage metrics for number of tokens
- Load balancing for multiple LLM models
- Rate limiting
- Authentication
- Load balancing

### Authentication

Application {Subscribtion Key} -> APIM (Gen AI Gateway) {Policy}  -> {Managed Identity -> RBAC} Azure AI service {OpenAI, Minstral, LLama}

- Create APIM -> uses GenAI capabilities to add authentication to AI services
- Create Foundry with models
- Policy that will use Managed identity to get access token to acess AI services
- Application will connect through APIM using subscribtion key through APIM

Create foundry
- create project
- New deployment
- Model -> deployment type -> deploy
Create APIM
- Multiple pricing tier
- Use consumption as its cheapest
- Security tab -> enable managed identiy -> Assighn the right RBAC (Cognitive services OpenAI USer) definie scope necessary
- assighn role to Managed identity
now Add API
Select Microsoft Foundry
or can use OpenAPI spec
switch to Full
can specify an OpenAPI specification URL or a JSON enpoint file
https://github.com/Azure/azure-rest-api-specs/tree/main/specification/cognitiveservices/data-plane
continas JSON file that contains the diffrence specs than can be used by openAI
if using spec change the URL of endpoint service to the one in foundry
but can also select microsoft foundry project
and set from there
need to configure APIM to get an authentication token from Managed identity to use AI services (Foundry)
can do this through configuring a policy
inbound policy, and add code in policy.xml
this policy will manage authentication using managed identity
so as we are using system assighned APIM can access the identity withouth the need to get resource ID
It will ask the identity to get authentication token to connect to cognitive service azure.com
so will then get the access token, naming it managed id access token
that acess token will be pased in the header as a variable called bearer
so when APIM calles the foundry service it will use that authentication token
You can import AI model endpoints deployed in Microsoft Foundry to your API Management instance as APIs. Use AI gateway policies and other capabilities in API Management to simplify integration, improve observability, and enhance control over the model endpoints.
https://learn.microsoft.com/en-us/azure/api-management/azure-ai-foundry-api

```
<inbound>
        <base />
        <authentication-managed-identity resource="https://cognitiveservices.azure.com"
            output-token-variable-name="managed-id-access-token" ignore-error="false" />
        <set-header name="Authorization" exists-action="override">
            <value>@("Bearer " + (string)context.Variables["managed-id-access-token"])</value>
        </set-header>
    </inbound>
```

Then create a subscribtion key to be used by APIM
select scope as API, select API just created -> create
copy the primary key
go to testing
select post get chat completion
in header add a header called api-key -> paste subscribtion value
in request body change the content string to message and system prompt you want, change model to model deployed in foundry
click send 

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

update env values to reflect your model then run main_SKD.py and run main_apim.py 