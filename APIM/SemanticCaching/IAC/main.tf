locals {
  resourcegroup            = coalesce(var.resourcegroup, "rg-tf-apim-genai-openai-${var.prefix}")
  apim_name                = coalesce(var.apim_name, "apim-genai-${var.prefix}")
  foundry_name             = coalesce(var.foundry_name, "foundry-ai-services-${var.prefix}")
  foundry_custom_subdomain = coalesce(var.foundry_custom_subdomain, "openai-${var.prefix}")
  use_aca                  = var.cache_backend == "aca"

  tags = {
    environment = "dev"
    ManagedBy   = "ore"
    workshop    = "apim"
  }
}

# Get current Azure client configuration
data "azurerm_client_config" "current" {}

resource "random_id" "random" {
  keepers = {
    # Generate a new ID only when a new resource group is defined
    resource_group = azurerm_resource_group.resourcegroup.name
  }

  byte_length = 8
}
resource "azurerm_resource_group" "resourcegroup" {
  name     = local.resourcegroup
  location = var.location
  tags     = local.tags
}

module "foundry" {
  source                                     = "./modules/Foundry"
  foundry_name                               = local.foundry_name
  foundry_cognitive_deployment_name          = var.foundry_cognitive_deployment_name
  location                                   = azurerm_resource_group.resourcegroup.location
  resourcegroup                              = azurerm_resource_group.resourcegroup.name
  foundry_custom_subdomain                   = local.foundry_custom_subdomain
  foundry_sku_name                           = var.foundry_sku_name
  foundry_cognitive_deployment_model_format  = var.foundry_cognitive_deployment_model_format
  foundry_cognitive_deployment_sku_name      = var.foundry_cognitive_deployment_sku_name
  foundry_cognitive_deployment_capacity      = var.foundry_cognitive_deployment_capacity
  foundry_cognitive_deployment_model_name    = var.foundry_cognitive_deployment_model_name
  foundry_cognitive_deployment_model_version = var.foundry_cognitive_deployment_model_version
  foundry_embedding_deployment_name          = var.foundry_embedding_deployment_name
  foundry_embedding_model_name               = var.foundry_embedding_model_name
  foundry_embedding_model_version            = var.foundry_embedding_model_version
  foundry_embedding_sku_name                 = var.foundry_embedding_sku_name
  foundry_embedding_capacity                 = var.foundry_embedding_capacity
}

module "apim" {
  source                      = "./modules/APIM"
  apim_name                   = local.apim_name
  location                    = azurerm_resource_group.resourcegroup.location
  resourcegroup               = azurerm_resource_group.resourcegroup.name
  apim_sku_name               = var.apim_sku_name
  prefix                      = var.prefix
  tags                        = local.tags
  apim_publisher_name         = var.apim_publisher_name
  apim_publisher_email        = var.apim_publisher_email
  apim_sub_name               = var.apim_sub_name
  apim_api_name               = var.apim_api_name
  foundry_management_endpoint = module.foundry.foundry_endpoint
  foundry_id                  = module.foundry.foundry_id
  foundry_embedding_endpoint  = module.foundry.foundry_embedding_endpoint
  redis_cache_enabled         = true
  redis_cache_id              = local.use_aca ? null : module.redis[0].redis_id
  redis_connection_string     = local.use_aca ? module.aca[0].aca_connection_string : module.redis[0].redis_connection_string
  apim_vnet_enabled           = local.use_aca
  apim_subnet_id              = local.use_aca ? module.aca[0].apim_subnet_id : null
}

module "redis" {
  count = local.use_aca ? 0 : 1

  source         = "./modules/Redis"
  redis_name     = coalesce(var.redis_name, "redis-${var.prefix}")
  redis_sku_name = var.redis_sku_name
  location       = azurerm_resource_group.resourcegroup.location
  resourcegroup  = azurerm_resource_group.resourcegroup.name
  tags           = local.tags
}

moved {
  from = module.redis
  to   = module.redis[0]
}

module "aca" {
  count = local.use_aca ? 1 : 0

  source                       = "./modules/ACA"
  location                     = azurerm_resource_group.resourcegroup.location
  resourcegroup                = azurerm_resource_group.resourcegroup.name
  prefix                       = var.prefix
  tags                         = local.tags
  redis_image                  = var.aca_redis_image
  vnet_address_prefix          = var.aca_vnet_address_prefix
  infrastructure_subnet_prefix = var.aca_infrastructure_subnet_prefix
  apim_subnet_prefix           = var.aca_apim_subnet_prefix
}
