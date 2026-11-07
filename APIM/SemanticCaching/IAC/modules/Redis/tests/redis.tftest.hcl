mock_provider "azurerm" {
  mock_resource "azurerm_managed_redis" {
    defaults = {
      hostname = "redis-test.uksouth.redis.azure.net"
      default_database = {
        port               = 10000
        primary_access_key = "mock-access-key"
      }
    }
  }
}

variables {
  redis_name     = "redis-test"
  redis_sku_name = "Balanced_B0"
  location       = "uksouth"
  resourcegroup  = "rg-redis-test"
  tags           = { environment = "test" }
}

run "semantic_cache" {
  command = apply

  assert {
    condition = (
      azurerm_managed_redis.redis.name == var.redis_name &&
      azurerm_managed_redis.redis.sku_name == var.redis_sku_name &&
      azurerm_managed_redis.redis.resource_group_name == var.resourcegroup &&
      azurerm_managed_redis.redis.location == var.location &&
      azurerm_managed_redis.redis.tags == var.tags
    )
    error_message = "Redis must use the supplied module inputs."
  }

  assert {
    condition = (
      azurerm_managed_redis.redis.default_database[0].client_protocol == "Encrypted" &&
      azurerm_managed_redis.redis.default_database[0].access_keys_authentication_enabled &&
      azurerm_managed_redis.redis.default_database[0].clustering_policy == "EnterpriseCluster" &&
      azurerm_managed_redis.redis.default_database[0].eviction_policy == "NoEviction" &&
      one(azurerm_managed_redis.redis.default_database[0].module).name == "RediSearch"
    )
    error_message = "APIM semantic caching requires TLS, access keys, and RediSearch with compatible database settings."
  }

  assert {
    condition     = output.redis_connection_string == "${output.redis_hostname}:${output.redis_port},password=mock-access-key,ssl=True,abortConnect=False"
    error_message = "The APIM connection string must contain the database endpoint, access key, and TLS settings."
  }
}
