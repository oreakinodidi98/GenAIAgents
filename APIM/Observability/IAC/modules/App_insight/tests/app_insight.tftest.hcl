mock_provider "azurerm" {
  mock_resource "azurerm_log_analytics_workspace" {
    defaults = {
      id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.OperationalInsights/workspaces/log-test"
    }
  }

  mock_resource "azurerm_application_insights" {
    defaults = {
      id                = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.Insights/components/app-test"
      connection_string = "InstrumentationKey=00000000-0000-0000-0000-000000000002;IngestionEndpoint=https://uksouth-1.in.applicationinsights.azure.com/"
    }
  }

  mock_resource "azurerm_api_management_logger" {
    defaults = {
      id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.ApiManagement/service/apim-test/loggers/app-insights-test"
    }
  }

  mock_data "azurerm_monitor_diagnostic_categories" {
    defaults = {
      log_category_types = ["GatewayLogs"]
      metrics            = ["AllMetrics"]
    }
  }
}

mock_provider "azapi" {}

variables {
  location                 = "uksouth"
  resourcegroup            = "rg-test"
  prefix                   = "test"
  tags                     = { environment = "test" }
  app_insights_name        = "app-test"
  log_analytics_name       = "log-test"
  retention_in_days        = 30
  apim_sampling_percentage = 50
  apim_id                  = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.ApiManagement/service/apim-test"
  apim_name                = "apim-test"
  apim_api_id              = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-test/providers/Microsoft.ApiManagement/service/apim-test/apis/openai"
  apim_principal_id        = "00000000-0000-0000-0000-000000000003"
}

run "workspace_and_managed_identity" {
  command = apply

  assert {
    condition = (
      azurerm_application_insights.app-insights.name == var.app_insights_name &&
      azurerm_application_insights.app-insights.workspace_id == output.log_analytics_id &&
      !azurerm_application_insights.app-insights.local_authentication_enabled &&
      azurerm_application_insights.app-insights.tags == var.tags &&
      azurerm_log_analytics_workspace.log-analytics.retention_in_days == var.retention_in_days &&
      azurerm_role_assignment.apim_metrics_publisher.principal_id == var.apim_principal_id &&
      azurerm_role_assignment.apim_metrics_publisher.scope == output.app_insights_id &&
      azurerm_role_assignment.apim_metrics_publisher.role_definition_name == "Monitoring Metrics Publisher" &&
      azurerm_api_management_logger.app_insights.application_insights[0].identity_client_id == "SystemAssigned" &&
      azurerm_api_management_logger.app_insights.application_insights[0].connection_string == output.app_insights_connection_string
    )
    error_message = "Application Insights must use the shared workspace and APIM managed identity with resource-scoped ingestion rights."
  }

  assert {
    condition = (
      azapi_resource.api_diagnostic.parent_id == var.apim_api_id &&
      jsondecode(azapi_resource.api_diagnostic.body).properties.loggerId == output.apim_logger_id &&
      jsondecode(azapi_resource.api_diagnostic.body).properties.metrics &&
      jsondecode(azapi_resource.api_diagnostic.body).properties.sampling.percentage == var.apim_sampling_percentage &&
      jsondecode(azapi_resource.api_diagnostic.body).properties.alwaysLog == "allErrors" &&
      !jsondecode(azapi_resource.api_diagnostic.body).properties.logClientIp &&
      jsondecode(azapi_resource.api_diagnostic.body).properties.frontend.request.body.bytes == 0 &&
      jsondecode(azapi_resource.api_diagnostic.body).properties.backend.response.body.bytes == 0 &&
      jsondecode(azapi_update_resource.enable-app-insights-withdimensions.body).properties.CustomMetricsOptedInType == "WithDimensions"
    )
    error_message = "API diagnostics must enable dimensioned custom metrics and sampling without logging request bodies."
  }

  assert {
    condition = (
      azurerm_monitor_diagnostic_setting.diagnostics_apim.target_resource_id == var.apim_id &&
      azurerm_monitor_diagnostic_setting.diagnostics_apim.log_analytics_workspace_id == output.log_analytics_id &&
      azurerm_monitor_diagnostic_setting.diagnostics_apim.log_analytics_destination_type == "Dedicated" &&
      one(azurerm_monitor_diagnostic_setting.diagnostics_apim.enabled_log).category == "GatewayLogs" &&
      one(azurerm_monitor_diagnostic_setting.diagnostics_apim.enabled_metric).category == "AllMetrics"
    )
    error_message = "APIM platform logs and metrics must be routed to the shared workspace."
  }
}

run "invalid_sampling" {
  command = plan
  variables {
    apim_sampling_percentage = 101
  }
  expect_failures = [var.apim_sampling_percentage]
}

run "invalid_retention" {
  command = plan
  variables {
    retention_in_days = 31
  }
  expect_failures = [var.retention_in_days]
}
