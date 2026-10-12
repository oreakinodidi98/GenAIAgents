data "azurerm_client_config" "current" {}
data "azurerm_subscription" "current" {}
data "azurerm_monitor_diagnostic_categories" "categories_apim" {
  resource_id = var.apim_id
}

resource "azurerm_log_analytics_workspace" "log-analytics" {
  name                = var.log_analytics_workspace_name
  location            = var.location
  resource_group_name = var.resourcegroup
  sku                 = "PerGB2018"
  retention_in_days   = 30
}
resource "azurerm_dashboard_grafana" "grafana" {
  name                              = var.azurerm_dashboard_grafana_name
  resource_group_name               = var.resourcegroup
  location                          = var.location
  grafana_major_version             = 11
  api_key_enabled                   = true
  deterministic_outbound_ip_enabled = true
  public_network_access_enabled     = true
  sku                               = "Standard"
  zone_redundancy_enabled           = false

  identity {
    type = "SystemAssigned"
  }
}
resource "azurerm_role_assignment" "role_grafana_admin" {
  scope                = azurerm_dashboard_grafana.grafana.id
  role_definition_name = "Grafana Admin"
  principal_id         = data.azurerm_client_config.current.object_id
}
resource "azurerm_role_assignment" "role_monitoring_reader" {
  scope                = data.azurerm_subscription.current.id # azurerm_resource_group.rg.id
  role_definition_name = "Monitoring Reader"
  principal_id         = azurerm_dashboard_grafana.grafana.identity.0.principal_id
}
resource "azurerm_monitor_diagnostic_setting" "diagnostics_apim" {
  name                           = var.azurerm_monitor_diagnostic_setting_name
  target_resource_id             = var.apim_id
  log_analytics_workspace_id     = azurerm_log_analytics_workspace.log-analytics.id
  log_analytics_destination_type = "Dedicated" # "AzureDiagnostics"

  dynamic "enabled_log" {
    for_each = data.azurerm_monitor_diagnostic_categories.categories_apim.log_category_types

    content {
      category = enabled_log.key
    }
  }

  dynamic "enabled_metric" {
    for_each = data.azurerm_monitor_diagnostic_categories.categories_apim.metrics

    content {
      category = enabled_metric.key
    }
  }

  lifecycle {
    ignore_changes = [
      log_analytics_destination_type
    ]
  }
}
resource "azurerm_application_insights" "app-insights" {
  name                          = var.application_insights_name
  location                      = var.location
  resource_group_name           = var.resourcegroup
  application_type              = "web"
  workspace_id                  = azurerm_log_analytics_workspace.log-analytics.id
  sampling_percentage           = null
  retention_in_days             = 30
  local_authentication_disabled = false
}

resource "azapi_update_resource" "enable-app-insights-withdimensions" {
  type        = "Microsoft.Insights/components@2020-02-02-preview"
  resource_id = azurerm_application_insights.app-insights.id

  body = {
    properties = {
      CustomMetricsOptedInType = "WithDimensions"
    }
  }
}
resource "azurerm_application_insights_workbook" "workbook" {
  name                = "85b3e8bb-fc93-40be-83f2-98f6bec18ba0"
  resource_group_name = var.resourcegroup
  location            = var.location
  display_name        = "openai-usage-analysis-workbook"
  category            = "OpenAI"
  source_id           = lower(azurerm_application_insights.app-insights.id)

  data_json = file("openai-usage-analysis-workbook.json")
}