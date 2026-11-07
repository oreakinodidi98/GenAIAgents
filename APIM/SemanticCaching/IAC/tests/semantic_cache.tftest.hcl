mock_provider "azurerm" {
  mock_resource "azurerm_ai_services" {
    defaults = {
      id       = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.CognitiveServices/accounts/foundry-test"
      endpoint = "https://foundry-test.cognitiveservices.azure.com/"
    }
  }

  mock_resource "azurerm_api_management" {
    defaults = {
      id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.ApiManagement/service/apim-test"
      identity = {
        principal_id = "00000000-0000-0000-0000-000000000002"
        tenant_id    = "00000000-0000-0000-0000-000000000001"
      }
    }
  }

  mock_resource "azurerm_api_management_api" {
    defaults = {
      id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.ApiManagement/service/apim-test/apis/apim-api-openai;rev=1"
    }
  }

  mock_resource "azurerm_managed_redis" {
    defaults = {
      id       = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.Cache/redisEnterprise/redis-test"
      hostname = "redis-test.uksouth.redis.azure.net"
      default_database = {
        port               = 10000
        primary_access_key = "mock-access-key"
      }
    }
  }

  mock_resource "azurerm_virtual_network" {
    defaults = {
      id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.Network/virtualNetworks/vnet-test"
    }
  }

  mock_resource "azurerm_subnet" {
    defaults = {
      id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.Network/virtualNetworks/vnet-test/subnets/subnet-test"
    }
  }

  mock_resource "azurerm_network_security_group" {
    defaults = {
      id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.Network/networkSecurityGroups/nsg-apim"
    }
  }

  mock_resource "azurerm_log_analytics_workspace" {
    defaults = {
      id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.OperationalInsights/workspaces/log-test"
    }
  }

  mock_resource "azurerm_container_app_environment" {
    defaults = {
      id                = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.App/managedEnvironments/aca-test"
      default_domain    = "aca-test.uksouth.azurecontainerapps.io"
      static_ip_address = "10.0.0.10"
    }
  }

  mock_resource "azurerm_container_app" {
    defaults = {
      ingress = {
        fqdn = "aca-redis-test.aca-test.uksouth.azurecontainerapps.io"
      }
    }
  }
}

mock_provider "random" {
  mock_resource "random_password" {
    defaults = {
      result = "mock-aca-password"
    }
  }
}

run "default_cache_connection" {
  command = apply

  variables {
    prefix = "cachetest"
  }

  assert {
    condition = (
      output.redis_name == "redis-cachetest" &&
      azurerm_resource_group.resourcegroup.name == "rg-tf-apim-genai-openai-cachetest" &&
      module.foundry.foundry_name == "foundry-ai-services-cachetest" &&
      module.foundry.foundry_custom_subdomain == "openai-cachetest"
    )
    error_message = "Default resource names must follow the supplied prefix."
  }

  assert {
    condition = (
      module.apim.redis_cache_id == output.redis_id &&
      module.apim.redis_cache_connection_string == output.redis_connection_string &&
      module.apim.apim_virtual_network_type == "None" &&
      length(module.aca) == 0
    )
    error_message = "APIM must register the Redis instance and its TLS connection string."
  }

  assert {
    condition = (
      module.apim.embeddings_backend_name == "apim-backend-openai-embedding" &&
      module.apim.embeddings_backend_url == output.foundry_embedding_endpoint &&
      output.foundry_embedding_endpoint == "https://foundry-test.cognitiveservices.azure.com/openai/deployments/text-embedding-3-small/embeddings"
    )
    error_message = "The policy's embeddings backend must use the deployed embeddings model."
  }
}

run "custom_cache_connection" {
  command = apply

  variables {
    resourcegroup                     = "rg-custom-cache"
    apim_name                         = "apim-custom-cache"
    foundry_name                      = "foundry-custom-cache"
    foundry_custom_subdomain          = "openai-custom-cache"
    redis_name                        = "redis-custom-cache"
    redis_sku_name                    = "Balanced_B1"
    foundry_embedding_deployment_name = "custom-embeddings"
  }

  assert {
    condition = (
      output.redis_name == "redis-custom-cache" &&
      azurerm_resource_group.resourcegroup.name == "rg-custom-cache" &&
      module.foundry.foundry_name == "foundry-custom-cache" &&
      module.foundry.foundry_custom_subdomain == "openai-custom-cache" &&
      module.apim.redis_cache_id == output.redis_id &&
      module.apim.redis_cache_connection_string == output.redis_connection_string &&
      module.apim.embeddings_backend_url == "https://foundry-test.cognitiveservices.azure.com/openai/deployments/custom-embeddings/embeddings"
    )
    error_message = "Resource name overrides must be preserved and APIM must remain connected to Redis."
  }
}

run "aca_cache_connection" {
  command = apply

  variables {
    cache_backend = "aca"
  }

  assert {
    condition = (
      length(module.redis) == 0 &&
      length(module.aca) == 1 &&
      module.apim.redis_cache_id == null &&
      module.apim.redis_cache_connection_string == module.aca[0].aca_connection_string &&
      output.redis_connection_string == module.aca[0].aca_connection_string &&
      output.redis_hostname == module.aca[0].aca_hostname &&
      output.redis_port == 6379 &&
      module.apim.apim_virtual_network_type == "External" &&
      module.apim.apim_subnet_id == module.aca[0].apim_subnet_id
    )
    error_message = "Selecting ACA must connect APIM through its private subnet without provisioning Managed Redis."
  }
}

run "invalid_backend" {
  command = plan

  variables {
    cache_backend = "invalid"
  }

  expect_failures = [var.cache_backend]
}
