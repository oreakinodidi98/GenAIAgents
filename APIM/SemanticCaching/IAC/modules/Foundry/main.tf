resource "azurerm_ai_services" "ai-services" {
  name                               = var.foundry_name
  location                           = var.location
  resource_group_name                = var.resourcegroup
  sku_name                           = var.foundry_sku_name
  local_authentication_enabled       = true
  public_network_access              = "Enabled"
  outbound_network_access_restricted = false
  custom_subdomain_name              = var.foundry_custom_subdomain
}

resource "azurerm_cognitive_deployment" "gpt-4o" {
  name                 = var.foundry_cognitive_deployment_name
  cognitive_account_id = azurerm_ai_services.ai-services.id

  sku {
    name     = var.foundry_cognitive_deployment_sku_name # "Standard" # DataZoneStandard, GlobalBatch, GlobalStandard and ProvisionedManaged
    capacity = var.foundry_cognitive_deployment_capacity
  }

  model {
    format  = var.foundry_cognitive_deployment_model_format
    name    = var.foundry_cognitive_deployment_model_name
    version = var.foundry_cognitive_deployment_model_version
  }
}

resource "azurerm_cognitive_deployment" "embeddings" {
  name                 = var.foundry_embedding_deployment_name
  cognitive_account_id = azurerm_ai_services.ai-services.id

  sku {
    name     = var.foundry_embedding_sku_name
    capacity = var.foundry_embedding_capacity
  }

  model {
    format  = "OpenAI"
    name    = var.foundry_embedding_model_name
    version = var.foundry_embedding_model_version
  }
}