locals {
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
  name     = var.resourcegroup
  location = var.location
  tags     = local.tags
}

module "foundry" {
  source                                     = "./modules/Foundry"
  foundry_name                               = var.foundry_name
  foundry_cognitive_deployment_name          = var.foundry_cognitive_deployment_name
  location                                   = var.location
  resourcegroup                              = var.resourcegroup
  foundry_custom_subdomain                   = var.foundry_custom_subdomain
  foundry_sku_name                           = var.foundry_sku_name
  foundry_cognitive_deployment_model_format  = var.foundry_cognitive_deployment_model_format
  foundry_cognitive_deployment_sku_name      = var.foundry_cognitive_deployment_sku_name
  foundry_cognitive_deployment_capacity      = var.foundry_cognitive_deployment_capacity
  foundry_cognitive_deployment_model_name    = var.foundry_cognitive_deployment_model_name
  foundry_cognitive_deployment_model_version = var.foundry_cognitive_deployment_model_version
}

module "apim" {
  source                      = "./modules/APIM"
  apim_name                   = var.apim_name
  location                    = var.location
  resourcegroup               = var.resourcegroup
  apim_sku_name               = var.apim_sku_name
  prefix                      = var.prefix
  tags                        = local.tags
  apim_publisher_name         = var.apim_publisher_name
  apim_publisher_email        = var.apim_publisher_email
  apim_sub_name               = var.apim_sub_name
  apim_api_name               = var.apim_api_name
  foundry_management_endpoint = module.foundry.foundry_endpoint
  foundry_id                  = module.foundry.foundry_id
  foundry_config              = var.foundry_config

}
