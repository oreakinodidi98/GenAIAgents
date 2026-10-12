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
output "apim_id" {
  value = module.apim.apim_id
}
output "app_insights_app_id" {
  value = module.monitor.app_insights_app_id
}
output "application_insights_connection_string" {
  value = module.monitor.application_insights_connection_string
}
output "log_analytics_workspace_id" {
  value = module.monitor.log_analytics_workspace_id
}
output "log_analytics_workspace_name" {
  value = module.monitor.log_analytics_workspace_name
}