# Agent Identity for AI Agents

Leveraging microsoft Agent Identity withing Foundry


## Use agent identities to access Azure resources in Microsoft Agent Framework

generating Azure token credentials through Microsoft.Identity.Web namespace and then use agent identities RBAC granted privileges to access Azure ADLS Gen2 storage

## Create a Foundry agent through agent identities

When you want to grant permisions to a resource using Microsfot entra for a service principla, normally use delegated prmisions. But this isnt the same for agent identity. Needs inheritable permissions on an agent identity blueprint to authorize a set delegate scopes.

E.G. agent identity requires permissions to create and deploy agents on Microsoft Foundry. This requires delegated permission for Azure Machine learning services

its not possible to assign the delegated permissions to a agent identity the way its done for a service principal.

With inheritable permissions agents automatically inherit permissions with the resulting access token's scp claim containing the inherited scopes and the inherited roles in the roles claim

## 2 Inheritance patterns

All Allowed and None.

All Allowed :- It inherits all the delegated permissions and roles for a resource app.

None :- Inherits no permissions and roles

Also have the following Inheritance permission options


allAllowedScope

- AllowedScope is the delegated permissions and acts on behalf of a signed in user and is the part of scp component in the access token.

allAllowedRoles
-  AllowedRoles is the app roles or application permissions and is the part of the roles component in the access token.

You can set them to allAllowed or none through the property kind.