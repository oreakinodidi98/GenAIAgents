resource "azurerm_api_management" "apim" {
  name                          = var.apim_name
  location                      = var.location
  resource_group_name           = var.resourcegroup
  publisher_name                = var.apim_publisher_name
  publisher_email               = var.apim_publisher_email
  sku_name                      = var.apim_sku_name # "Consumption_0" # "Developer_1"
  virtual_network_type          = "None"        # None, External, Internal
  public_network_access_enabled = true          # false applies only when using private endpoint as the exclusive access method

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "Cognitive-Services-OpenAI-User" {
  scope                = var.foundry_id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_api_management.apim.identity.0.principal_id
}
resource "azurerm_role_assignment" "Monitoring-Metrics-Publisher" {
  scope                = var.app_insights_app_id
  role_definition_name = "Monitoring Metrics Publisher"
  principal_id         = azurerm_api_management.apim.identity.0.principal_id
}
resource "azurerm_api_management_api" "apim-api-openai" {
  name                  = var.apim_api_name
  resource_group_name   = azurerm_api_management.apim.resource_group_name
  api_management_name   = azurerm_api_management.apim.name
  revision              = "1"
  description           = "Azure OpenAI APIs for completions and search"
  display_name          = "OpenAI"
  path                  = "openai"
  protocols             = ["https"]
  service_url           = "${var.foundry_management_endpoint}openai"
  subscription_required = true
  api_type              = "http"

  import {
    content_format = "openapi-link"
    content_value  = "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/refs/heads/main/specification/cognitiveservices/data-plane/AzureOpenAI/inference/stable/2024-10-21/inference.json"
  }

  subscription_key_parameter_names {
    header = "api-key"
    query  = "api-key"
  }
}
resource "azurerm_api_management_subscription" "apim-api-subscription-openai" {
  display_name        = var.apim_sub_name
  api_management_name = azurerm_api_management.apim.name
  resource_group_name = azurerm_api_management.apim.resource_group_name
  api_id              = replace(azurerm_api_management_api.apim-api-openai.id, "/;rev=.*/", "")
  allow_tracing       = true
  state               = "active"
}
resource "azurerm_api_management_api_policy" "apim-openai-policy-openai" {
  api_name            = azurerm_api_management_api.apim-api-openai.name
  api_management_name = azurerm_api_management_api.apim-api-openai.api_management_name
  resource_group_name = azurerm_api_management_api.apim-api-openai.resource_group_name

  xml_content = file("policy.xml")
}
resource "azurerm_api_management_logger" "apim-logger" {
  name                = "apim-logger"
  api_management_name = azurerm_api_management.apim.name
  resource_group_name = azurerm_api_management.apim.resource_group_name
  buffered            = false
  resource_id         = var.app_insights_app_id

  application_insights {
    connection_string = var.application_insights_connection_string
  }
}
resource "azurerm_api_management_diagnostic" "apim-diagnostic" {
  identifier                = "applicationinsights" # "azuremonitor"
  resource_group_name       = azurerm_api_management.apim.resource_group_name
  api_management_name       = azurerm_api_management.apim.name
  api_management_logger_id  = azurerm_api_management_logger.apim-logger.id
  sampling_percentage       = 100
  always_log_errors         = true
  log_client_ip             = true
  verbosity                 = "verbose"
  http_correlation_protocol = "W3C"

  frontend_request {
    body_bytes = 8192
    headers_to_log = [
      "Content-type",
      "accept",
      "origin",
      "User-agent",
      "x-ms-region",
      "x-ratelimit-remaining-tokens",
      "x-ratelimit-remaining-requests"
    ]
  }

  frontend_response {
    body_bytes = 8192
    headers_to_log = [
      "Content-type",
      "accept",
      "origin",
      "User-agent",
      "x-ms-region",
      "x-ratelimit-remaining-tokens",
      "x-ratelimit-remaining-requests"
    ]
  }

  backend_request {
    body_bytes = 8192
    headers_to_log = [
      "Content-type",
      "accept",
      "origin",
      "User-agent",
      "x-ms-region",
      "x-ratelimit-remaining-tokens",
      "x-ratelimit-remaining-requests"
    ]
  }

  backend_response {
    body_bytes = 8192
    headers_to_log = [
      "Content-type",
      "accept",
      "origin",
      "User-agent",
      "x-ms-region",
      "x-ratelimit-remaining-tokens",
      "x-ratelimit-remaining-requests"
    ]
  }
}