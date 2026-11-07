output "grafana_id" {
  value = azurerm_dashboard_grafana.grafana.id
}

output "grafana_name" {
  value = azurerm_dashboard_grafana.grafana.name
}

output "grafana_endpoint" {
  value = azurerm_dashboard_grafana.grafana.endpoint
}

output "grafana_principal_id" {
  value = azurerm_dashboard_grafana.grafana.identity[0].principal_id
}

output "monitoring_scope_id" {
  value = azurerm_role_assignment.role_monitoring_reader.scope
}

output "grafana_admin_object_id" {
  value = azurerm_role_assignment.role_grafana_admin.principal_id
}