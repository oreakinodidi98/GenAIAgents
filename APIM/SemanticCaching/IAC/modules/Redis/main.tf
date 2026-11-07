terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.67.0, < 5.0.0"
    }
  }
}

resource "azurerm_managed_redis" "redis" {
  name                      = var.redis_name
  location                  = var.location
  resource_group_name       = var.resourcegroup
  sku_name                  = var.redis_sku_name
  high_availability_enabled = true
  public_network_access     = "Enabled"
  tags                      = var.tags

  default_database {
    # APIM's external cache connection currently requires access-key authentication.
    access_keys_authentication_enabled = true
    client_protocol                    = "Encrypted"
    clustering_policy                  = "EnterpriseCluster"
    eviction_policy                    = "NoEviction"

    module {
      name = "RediSearch"
    }
  }
}