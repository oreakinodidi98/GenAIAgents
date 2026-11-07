terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.67.0, < 5.0.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.5.1"
    }
  }
}

resource "azurerm_virtual_network" "vnet-aca" {
  name                = "vnet-aca-${var.prefix}"
  resource_group_name = var.resourcegroup
  location            = var.location
  address_space       = [var.vnet_address_prefix]
  tags                = var.tags
}

resource "azurerm_subnet" "snet-aca" {
  name                 = "snet-aca"
  resource_group_name  = azurerm_virtual_network.vnet-aca.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet-aca.name
  address_prefixes     = [var.infrastructure_subnet_prefix]

  delegation {
    name = "container-apps"
    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_subnet" "snet-apim" {
  name                 = "snet-apim"
  resource_group_name  = azurerm_virtual_network.vnet-aca.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet-aca.name
  address_prefixes     = [var.apim_subnet_prefix]
}

resource "azurerm_log_analytics_workspace" "aca" {
  name                = "log-aca-${var.prefix}"
  location            = var.location
  resource_group_name = var.resourcegroup
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_container_app_environment" "aca-env" {
  name                           = "aca-environment-${var.prefix}"
  location                       = var.location
  resource_group_name            = var.resourcegroup
  log_analytics_workspace_id     = azurerm_log_analytics_workspace.aca.id
  zone_redundancy_enabled        = false
  internal_load_balancer_enabled = true
  infrastructure_subnet_id       = azurerm_subnet.snet-aca.id
  tags                           = var.tags

  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }
}

resource "azurerm_private_dns_zone" "aca" {
  name                = azurerm_container_app_environment.aca-env.default_domain
  resource_group_name = var.resourcegroup
  tags                = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "aca" {
  name                  = "aca-vnet-link"
  resource_group_name   = var.resourcegroup
  private_dns_zone_name = azurerm_private_dns_zone.aca.name
  virtual_network_id    = azurerm_virtual_network.vnet-aca.id
  registration_enabled  = false
  tags                  = var.tags
}

resource "azurerm_private_dns_a_record" "aca" {
  name                = "*"
  zone_name           = azurerm_private_dns_zone.aca.name
  resource_group_name = var.resourcegroup
  ttl                 = 300
  records             = [azurerm_container_app_environment.aca-env.static_ip_address]
  tags                = var.tags
}

resource "random_password" "redis" {
  length  = 32
  special = false
}

resource "azurerm_container_app" "aca-redis-stack" {
  name                         = "aca-redis-${var.prefix}"
  container_app_environment_id = azurerm_container_app_environment.aca-env.id
  resource_group_name          = var.resourcegroup
  revision_mode                = "Single"
  workload_profile_name        = "Consumption"
  tags                         = var.tags

  secret {
    name  = "redis-password"
    value = random_password.redis.result
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name    = "redis"
      image   = var.redis_image
      cpu     = 0.5
      memory  = "1Gi"
      command = ["/bin/sh", "-c"]
      args    = [trimspace(file("${path.module}/redis-start.sh"))]

      env {
        name        = "REDIS_PASSWORD"
        secret_name = "redis-password"
      }
    }
  }

  ingress {
    # "External" means outside the app environment; its load balancer is VNet-only.
    external_enabled = true
    exposed_port     = 6379
    target_port      = 6379
    transport        = "tcp"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
}