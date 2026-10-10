locals {
  tags = {
    environment     = "dev"
    ManagedBy       = "Ore"
    workshop        = "ACA Terraform"
    SecurityControl = "Ignore"
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

module "aca" {
  source              = "./modules/aca"
  environment_name    = var.environment_name
  aca_gemma_name      = var.aca_gemma_name
  aca_open_webui_name = var.aca_open_webui_name
  aca_qwen_name       = var.aca_qwen_name
  location            = var.location
  resourcegroup       = azurerm_resource_group.resourcegroup.name
  resourcegroup_id    = azurerm_resource_group.resourcegroup.id
  aca_subnet_id       = module.network.aca_subnet_id
}

module "appservice" {
  source          = "./modules/appservice"
  plan_name       = var.plan_name
  appservice_name = var.appservice_name
  location        = var.location
  resourcegroup   = azurerm_resource_group.resourcegroup.name
  os_type         = var.os_type
  sku_kind        = var.sku_kind
}

module "foundry" {
  source                = "./modules/foundry"
  location              = var.location
  resourcegroup         = azurerm_resource_group.resourcegroup.name
  foundry_name          = var.foundry_name
  foundry_project_name  = var.foundry_project_name
  custom_subdomain_name = var.custom_subdomain_name
}

module "cosmosDB" {
  source            = "./modules/cosmosDB"
  location          = var.location
  resourcegroup     = azurerm_resource_group.resourcegroup.name
  cosmos_name       = var.cosmos_name
  cosmos_kind       = var.cosmos_kind
  cosmos_offer_type = var.cosmos_offer_type
}

module "network" {
  source        = "./modules/network"
  subnet_name   = var.subnet_name
  vnet_name     = var.vnet_name
  resourcegroup = azurerm_resource_group.resourcegroup.name
  location      = var.location
}