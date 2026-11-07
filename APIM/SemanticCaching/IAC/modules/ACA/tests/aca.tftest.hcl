mock_provider "azurerm" {
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

variables {
  prefix                       = "test"
  location                     = "uksouth"
  resourcegroup                = "rg-test"
  tags                         = { environment = "test" }
  redis_image                  = "redis:8.2.3"
  vnet_address_prefix          = "10.0.0.0/16"
  infrastructure_subnet_prefix = "10.0.0.0/23"
  apim_subnet_prefix           = "10.0.2.0/24"
}

run "private_redis_cache" {
  command = apply

  assert {
    condition = (
      azurerm_container_app_environment.aca-env.internal_load_balancer_enabled &&
      azurerm_container_app_environment.aca-env.infrastructure_subnet_id == azurerm_subnet.snet-aca.id &&
      azurerm_container_app.aca-redis-stack.ingress[0].transport == "tcp" &&
      azurerm_container_app.aca-redis-stack.ingress[0].exposed_port == 6379 &&
      azurerm_container_app.aca-redis-stack.ingress[0].external_enabled &&
      one(azurerm_private_dns_a_record.aca.records) == "10.0.0.10" &&
      azurerm_private_dns_zone_virtual_network_link.aca.virtual_network_id == azurerm_virtual_network.vnet-aca.id
    )
    error_message = "Redis must be reachable through private VNet ingress and DNS, not a public environment."
  }

  assert {
    condition = (
      azurerm_subnet.snet-aca.address_prefixes == tolist([var.infrastructure_subnet_prefix]) &&
      azurerm_subnet.snet-apim.address_prefixes == tolist([var.apim_subnet_prefix]) &&
      length(azurerm_subnet.snet-apim.delegation) == 0
    )
    error_message = "ACA and APIM must use separate subnets, and APIM's subnet must not be delegated."
  }

  assert {
    condition = (
      azurerm_container_app.aca-redis-stack.name == "aca-redis-test" &&
      azurerm_container_app.aca-redis-stack.tags == var.tags &&
      azurerm_container_app.aca-redis-stack.template[0].min_replicas == 1 &&
      azurerm_container_app.aca-redis-stack.template[0].max_replicas == 1 &&
      azurerm_container_app.aca-redis-stack.template[0].container[0].image == var.redis_image &&
      azurerm_container_app.aca-redis-stack.template[0].container[0].args[0] == trimspace(file("redis-start.sh")) &&
      one(azurerm_container_app.aca-redis-stack.template[0].container[0].env).secret_name == "redis-password" &&
      one(azurerm_container_app.aca-redis-stack.secret).value == random_password.redis.result
    )
    error_message = "Redis must use the supplied inputs, tested startup command, a secret, and one replica."
  }

  assert {
    condition     = output.aca_connection_string == "${output.aca_hostname}:6379,password=mock-aca-password,ssl=False,abortConnect=False"
    error_message = "APIM must receive the private Redis endpoint and generated password."
  }
}
