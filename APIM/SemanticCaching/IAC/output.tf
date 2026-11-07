output "apim_resource_gateway_url" {
  value = module.apim.apim_resource_gateway_url
}

output "apim_subscription_key" {
  value     = module.apim.apim_subscription_key
  sensitive = true
}
output "apim_management_endpoint" {
  value = module.apim.apim_management_endpoint
}
output "apim_publisher_email" {
  value = module.apim.apim_publisher_email
}
output "foundry_endpoint" {
  value = module.foundry.foundry_endpoint
}
output "foundry_name" {
  value = module.foundry.foundry_name
}
output "foundry_cognitive_deployment_name" {
  value = module.foundry.foundry_cognitive_deployment_name
}
output "foundry_custom_subdomain" {
  value = module.foundry.foundry_custom_subdomain
}
output "foundry_id" {
  value = module.foundry.foundry_id
}

output "redis_id" {
  value = local.use_aca ? module.aca[0].aca_id : module.redis[0].redis_id
}

output "redis_name" {
  value = local.use_aca ? module.aca[0].aca_name : module.redis[0].redis_name
}

output "redis_hostname" {
  value = local.use_aca ? module.aca[0].aca_hostname : module.redis[0].redis_hostname
}

output "redis_port" {
  value = local.use_aca ? 6379 : module.redis[0].redis_port
}

output "redis_connection_string" {
  value     = local.use_aca ? module.aca[0].aca_connection_string : module.redis[0].redis_connection_string
  sensitive = true
}

output "foundry_embedding_deployment_name" {
  value = module.foundry.foundry_embedding_deployment_name
}

output "foundry_embedding_endpoint" {
  value = module.foundry.foundry_embedding_endpoint
}

output "aca_environment_id" {
  value = local.use_aca ? module.aca[0].aca_environment_id : null
}

output "aca_vnet_id" {
  value = local.use_aca ? module.aca[0].aca_vnet_id : null
}
