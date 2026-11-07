---
title: Token Limit Policy with Azure API Management
description: A hands-on walkthrough of using APIM Token limit policy.
---

llm models have a limitation for number of tokens that can be consumed
can apply a policy im APIM to limit the amount off tokens consumed by app or user
uses a counter key to configure policy
so token counted for each user
can configure to count the exact number of tokens or remaining number of tokens 
can then get this in responce of http requests

## demo

create APIM -> rate limit policy works with any SKU except consumtion
create foundry
apply policy

<azure-openai-token-limit
            counter-key="@(context.Request.IpAddress)"
            tokens-per-minute="500"
            estimate-prompt-tokens="false"
            remaining-tokens-variable-name="remainingTokens">
        </azure-openai-token-limit>
watches for the IP adress of each connected user
sets limit to 500 per minute
wont estimate the prompt tokens, so can excede maximum allowed tokens because it allows request to be sent to azure openai then counts the remaining tokens