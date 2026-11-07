terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.81.0, < 5.0.0"
    }
    azapi = {
      source  = "azure/azapi"
      version = "~> 1.0"
    }
  }
}

resource "azurerm_log_analytics_workspace" "log-analytics" {
  name                = var.log_analytics_name
  location            = var.location
  resource_group_name = var.resourcegroup
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_in_days
  tags                = var.tags
}

resource "azurerm_application_insights" "app-insights" {
  name                         = var.app_insights_name
  location                     = var.location
  resource_group_name          = var.resourcegroup
  application_type             = "web"
  workspace_id                 = azurerm_log_analytics_workspace.log-analytics.id
  sampling_percentage          = 100
  retention_in_days            = var.retention_in_days
  local_authentication_enabled = false
  tags                         = var.tags
}

resource "azapi_update_resource" "enable-app-insights-withdimensions" {
  type        = "Microsoft.Insights/components@2020-02-02-preview"
  resource_id = azurerm_application_insights.app-insights.id

  body = jsonencode({
    properties = {
      CustomMetricsOptedInType = "WithDimensions"
    }
  })
}

resource "azurerm_role_assignment" "apim_metrics_publisher" {
  scope                = azurerm_application_insights.app-insights.id
  role_definition_name = "Monitoring Metrics Publisher"
  principal_id         = var.apim_principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_api_management_logger" "app_insights" {
  name                = "app-insights-${var.prefix}"
  resource_group_name = var.resourcegroup
  api_management_name = var.apim_name
  resource_id         = azurerm_application_insights.app-insights.id

  application_insights {
    connection_string  = azurerm_application_insights.app-insights.connection_string
    identity_client_id = "SystemAssigned"
  }

  depends_on = [azurerm_role_assignment.apim_metrics_publisher]
}

# AzureRM's API diagnostic resource does not expose the custom-metrics switch.
resource "azapi_resource" "api_diagnostic" {
  type      = "Microsoft.ApiManagement/service/apis/diagnostics@2022-08-01"
  name      = "applicationinsights"
  parent_id = var.apim_api_id

  body = jsonencode({
    properties = {
      loggerId                = azurerm_api_management_logger.app_insights.id
      metrics                 = true
      alwaysLog               = "allErrors"
      logClientIp             = false
      httpCorrelationProtocol = "W3C"
      verbosity               = "information"
      sampling = {
        samplingType = "fixed"
        percentage   = var.apim_sampling_percentage
      }
      frontend = {
        request  = { body = { bytes = 0 }, headers = [] }
        response = { body = { bytes = 0 }, headers = [] }
      }
      backend = {
        request  = { body = { bytes = 0 }, headers = [] }
        response = { body = { bytes = 0 }, headers = [] }
      }
    }
  })

  depends_on = [azapi_update_resource.enable-app-insights-withdimensions]
}
data "azurerm_monitor_diagnostic_categories" "categories_apim" {
  resource_id = var.apim_id
}

resource "azurerm_monitor_diagnostic_setting" "diagnostics_apim" {
  name                           = "diagnostic-settings-az-apim"
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

}