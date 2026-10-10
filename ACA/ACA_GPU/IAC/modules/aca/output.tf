output "aca_gemma4_31b_it_a100_fqdn" {
  value = azurerm_container_app.aca_gemma4_31b_it_a100.ingress.0.fqdn
}
output "supported_workload_profiles" {
  value = "az containerapp env workload-profile list-supported --location ${azurerm_resource_group.rg.location} -o table"
}
output "aca_open_webui_fqdn" {
  value = azurerm_container_app.open_webui.ingress.0.fqdn
}
output "aca_qwen_36_35b_a100_fqdn" {
  value = azurerm_container_app.aca_qwen_36_35b_a100.ingress.0.fqdn
}