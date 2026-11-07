resource "azurerm_api_management" "apim" {
  name                          = var.apim_name
  location                      = var.location
  resource_group_name           = var.resourcegroup
  publisher_name                = var.apim_publisher_name
  publisher_email               = var.apim_publisher_email
  sku_name                      = var.apim_sku_name # "Consumption_0" # "Developer_1"
  virtual_network_type          = var.apim_vnet_enabled ? "External" : "None"
  public_network_access_enabled = true # false applies only when using private endpoint as the exclusive access method

  dynamic "virtual_network_configuration" {
    for_each = var.apim_vnet_enabled ? [var.apim_subnet_id] : []
    content {
      subnet_id = virtual_network_configuration.value
    }
  }

  identity {
    type = "SystemAssigned"
  }

  lifecycle {
    precondition {
      condition = !var.apim_vnet_enabled || (
        startswith(var.apim_sku_name, "Developer_") ||
        startswith(var.apim_sku_name, "Premium_")
      )
      error_message = "The private ACA cache requires classic Developer or Premium APIM for VNet injection."
    }
    precondition {
      condition     = !var.apim_vnet_enabled || var.apim_subnet_id != null
      error_message = "APIM VNet injection requires a non-delegated subnet ID."
    }
  }

  depends_on = [azurerm_subnet_network_security_group_association.apim]
}

resource "azurerm_network_security_group" "apim" {
  count = var.apim_vnet_enabled ? 1 : 0

  name                = "nsg-apim-${var.prefix}"
  location            = var.location
  resource_group_name = var.resourcegroup
  tags                = var.tags

  security_rule {
    name                       = "AllowGatewayHTTPS"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "Internet"
    destination_address_prefix = "VirtualNetwork"
  }

  security_rule {
    name                       = "AllowAPIMManagement"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3443"
    source_address_prefix      = "ApiManagement"
    destination_address_prefix = "VirtualNetwork"
  }

  security_rule {
    name                       = "AllowLoadBalancer"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "6390"
    source_address_prefix      = "AzureLoadBalancer"
    destination_address_prefix = "VirtualNetwork"
  }
}

resource "azurerm_subnet_network_security_group_association" "apim" {
  count = var.apim_vnet_enabled ? 1 : 0

  subnet_id                 = var.apim_subnet_id
  network_security_group_id = azurerm_network_security_group.apim[0].id
}

resource "azurerm_role_assignment" "Cognitive-Services-OpenAI-User" {
  scope                = var.foundry_id
  role_definition_name = "Cognitive Services OpenAI User"
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

  xml_content = file("${path.module}/../../../policy/policy.xml")

  depends_on = [
    azurerm_api_management_backend.apim-backend-openai-embedding,
    azurerm_api_management_redis_cache.redis,
    azurerm_role_assignment.Cognitive-Services-OpenAI-User,
  ]
}

resource "azurerm_api_management_backend" "apim-backend-openai-embedding" {
  name                = "apim-backend-openai-embedding"
  resource_group_name = var.resourcegroup # azurerm_api_management.apim.resource_group_name
  api_management_name = azurerm_api_management.apim.name
  protocol            = "http"
  url                 = var.foundry_embedding_endpoint
}

resource "azurerm_api_management_redis_cache" "redis" {
  count = var.redis_cache_enabled ? 1 : 0

  name              = "redis-semantic-cache"
  api_management_id = azurerm_api_management.apim.id
  connection_string = var.redis_connection_string
  redis_cache_id    = var.redis_cache_id
  cache_location    = "default"
  description       = "Redis with vector search for semantic caching"
}