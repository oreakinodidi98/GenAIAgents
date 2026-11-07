output "apim_publisher_email" {
  value = var.apim_publisher_email
}

output "apim_resource_gateway_url" {
  value = azurerm_api_management.apim.gateway_url
}

output "apim_management_endpoint" {
  value = azurerm_api_management.apim.management_api_url
}
output "apim_subscription_key" {
  value = azurerm_api_management_subscription.apim-api-subscription-openai.primary_key
}

output "redis_cache_id" {
  value = var.redis_cache_enabled ? azurerm_api_management_redis_cache.redis[0].redis_cache_id : null
}

output "redis_cache_connection_string" {
  value     = var.redis_cache_enabled ? azurerm_api_management_redis_cache.redis[0].connection_string : null
  sensitive = true
}

output "embeddings_backend_name" {
  value = azurerm_api_management_backend.apim-backend-openai-embedding.name
}

output "embeddings_backend_url" {
  value = azurerm_api_management_backend.apim-backend-openai-embedding.url
}

output "apim_virtual_network_type" {
  value = azurerm_api_management.apim.virtual_network_type
}

output "apim_subnet_id" {
  value = var.apim_vnet_enabled ? azurerm_api_management.apim.virtual_network_configuration[0].subnet_id : null
}