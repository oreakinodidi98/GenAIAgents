variable "location" {
}
variable "resourcegroup" {
}
variable "prefix" {
}
variable "tags" {
  type = map(string)
}
variable "log_analytics_workspace_name" {
  description = "Name of the Log Analytics workspace for monitoring"
  type        = string
}
variable "azurerm_dashboard_grafana_name" {
  description = "Name of the Azure Dashboard Grafana instance"
  type        = string
}
variable "apim_id" {
  description = "ID of the API Management instance"
  type        = string
}
variable "azurerm_monitor_diagnostic_setting_name" {
  description = "Name of the Azure Monitor Diagnostic Setting for the API Management instance"
  type        = string
}
variable "application_insights_name" {
  description = "Name of the Application Insights instance for monitoring"
  type        = string
}