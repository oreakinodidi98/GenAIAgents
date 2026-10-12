output "app_insights_app_id" {
  value = azurerm_application_insights.app-insights.app_id
}
output "app_insights_resource_name" {
  value = azurerm_application_insights.app-insights.name
}
output "log_analytics_workspace_id" {
  value = azurerm_log_analytics_workspace.log-analytics.id
}
output "log_analytics_workspace_name" {
  value = azurerm_log_analytics_workspace.log-analytics.name
}
output "application_insights_connection_string" {
  value = azurerm_application_insights.app-insights.connection_string
}