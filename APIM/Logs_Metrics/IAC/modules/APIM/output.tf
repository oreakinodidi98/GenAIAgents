output "apim_publisher_email" {
  value = var.apim_publisher_email
}

output "apim_resource_gateway_url" {
  value = azurerm_api_management.apim.gateway_url
}

output "apim_management_endpoint" {
  value = azurerm_api_management.apim.management_endpoint
}
output "apim_subscription_key" {
  value =  azurerm_api_management_subscription.apim-api-subscription-openai.primary_key
  sensitive = true
}
output "apim_id" {
  value = azurerm_api_management.apim.id
}