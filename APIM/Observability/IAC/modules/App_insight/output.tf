output "app_insights_id" {
  value = azurerm_application_insights.app-insights.id
}

output "app_insights_name" {
  value = azurerm_application_insights.app-insights.name
}

output "app_insights_connection_string" {
  value     = azurerm_application_insights.app-insights.connection_string
  sensitive = true
}

output "log_analytics_id" {
  value = azurerm_log_analytics_workspace.log-analytics.id
}

output "log_analytics_name" {
  value = azurerm_log_analytics_workspace.log-analytics.name
}

output "apim_logger_id" {
  value = azurerm_api_management_logger.app_insights.id
}

output "apim_api_diagnostic_id" {
  value = azapi_resource.api_diagnostic.id
}

output "apim_id" {
  value = azurerm_monitor_diagnostic_setting.diagnostics_apim.target_resource_id
}

output "apim_api_id" {
  value = azapi_resource.api_diagnostic.parent_id
}

output "apim_principal_id" {
  value = azurerm_role_assignment.apim_metrics_publisher.principal_id
}