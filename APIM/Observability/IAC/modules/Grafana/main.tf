terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.81.0, < 5.0.0"
    }
  }
}

resource "azurerm_dashboard_grafana" "grafana" {
  name                              = var.grafana_name
  resource_group_name               = var.resourcegroup
  location                          = var.location
  grafana_major_version             = var.grafana_major_version
  api_key_enabled                   = false
  deterministic_outbound_ip_enabled = true
  public_network_access_enabled     = true
  sku                               = "Standard"
  zone_redundancy_enabled           = false
  tags                              = var.tags

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "role_grafana_admin" {
  scope                = azurerm_dashboard_grafana.grafana.id
  role_definition_name = "Grafana Admin"
  principal_id         = var.grafana_admin_object_id
}

resource "azurerm_role_assignment" "role_monitoring_reader" {
  scope                = var.monitoring_scope_id
  role_definition_name = "Monitoring Reader"
  principal_id         = azurerm_dashboard_grafana.grafana.identity.0.principal_id
  principal_type       = "ServicePrincipal"
}