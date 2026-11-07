mock_provider "azurerm" {
  mock_resource "azurerm_dashboard_grafana" {
    defaults = {
      id       = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.Dashboard/grafana/grafana-test"
      endpoint = "https://grafana-test.grafana.azure.com"
      identity = {
        principal_id = "00000000-0000-0000-0000-000000000002"
        tenant_id    = "00000000-0000-0000-0000-000000000001"
      }
    }
  }
}

variables {
  location                = "uksouth"
  resourcegroup           = "rg-test"
  tags                    = { environment = "test" }
  grafana_name            = "grafana-test"
  grafana_major_version   = "11"
  grafana_admin_object_id = "00000000-0000-0000-0000-000000000003"
  monitoring_scope_id     = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test"
}

run "resource_group_monitoring" {
  command = apply

  assert {
    condition = (
      output.grafana_name == var.grafana_name &&
      output.grafana_endpoint == "https://grafana-test.grafana.azure.com" &&
      azurerm_dashboard_grafana.grafana.location == var.location &&
      azurerm_dashboard_grafana.grafana.resource_group_name == var.resourcegroup &&
      azurerm_dashboard_grafana.grafana.tags == var.tags &&
      !azurerm_dashboard_grafana.grafana.api_key_enabled &&
      azurerm_role_assignment.role_grafana_admin.scope == output.grafana_id &&
      azurerm_role_assignment.role_grafana_admin.principal_id == var.grafana_admin_object_id &&
      azurerm_role_assignment.role_grafana_admin.role_definition_name == "Grafana Admin" &&
      azurerm_role_assignment.role_monitoring_reader.scope == var.monitoring_scope_id &&
      azurerm_role_assignment.role_monitoring_reader.principal_id == output.grafana_principal_id &&
      azurerm_role_assignment.role_monitoring_reader.role_definition_name == "Monitoring Reader"
    )
    error_message = "Grafana must use the supplied inputs, Entra administrator, and resource-group-scoped managed identity read access."
  }
}

run "grafana_12" {
  command = apply
  variables {
    grafana_major_version = "12"
  }
  assert {
    condition     = azurerm_dashboard_grafana.grafana.grafana_major_version == "12"
    error_message = "The supported Grafana version override must be respected."
  }
}

run "unsupported_version" {
  command = plan
  variables {
    grafana_major_version = "10"
  }
  expect_failures = [var.grafana_major_version]
}
