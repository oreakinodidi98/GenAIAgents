output "foundry_name" {
  value = var.foundry_name
}
output "foundry_cognitive_deployment_name" {
  value = var.foundry_cognitive_deployment_name
}
output "foundry_custom_subdomain" {
  value = var.foundry_custom_subdomain
}
output "foundry_endpoint" {
  value = azurerm_ai_services.ai-services.endpoint
}
output "foundry_id" {
  value = azurerm_ai_services.ai-services.id
}