# =============================================================================
# OUTPUT VALUES
# These outputs provide important information for connecting your application
# =============================================================================

# -----------------------------------------------------------------------------
# Foundry Resource Outputs
# -----------------------------------------------------------------------------

output "foundry_endpoint" {
  value = module.foundry.foundry_endpoint
}

output "foundry_api_key" {
  value     = module.foundry.foundry_api_key
  sensitive = true
}

output "foundry_project_endpoint" {
  value = module.foundry.foundry_project_endpoint
}

output "llm_model_deployment_name_kimi" {
  value = module.foundry.llm_model_deployment_name_kimi
}

output "llm_model_deployment_name_chatgpt" {
  value = module.foundry.llm_model_deployment_name_chatgpt
}

# -----------------------------------------------------------------------------
# Cosmos DB Resource Outputs
# -----------------------------------------------------------------------------
output "cosmosdb_endpoint" {
  value = module.cosmosDB.cosmosdb_endpoint
}

output "cosmosdb_key" {
  value     = module.cosmosDB.cosmosdb_key
  sensitive = true
}
# -----------------------------------------------------------------------------
# App service Resource Outputs
# -----------------------------------------------------------------------------
output "app_service_mcp_server_open_web_search_fqdn" {
  value = module.appservice.app_service_mcp_server_open_web_search_fqdn
}
# -----------------------------------------------------------------------------
# ACA Resource Outputs
# -----------------------------------------------------------------------------
output "aca_gemma4_31b_it_a100_fqdn" {
  value = module.aca.aca_gemma4_31b_it_a100_fqdn
}
output "supported_workload_profiles" {
  value = module.aca.supported_workload_profiles
}

output "aca_open_webui_fqdn" {
  value = module.aca.aca_open_webui_fqdn
}

output "aca_qwen_36_35b_a100_fqdn" {
  value = module.aca.aca_qwen_36_35b_a100_fqdn
}
# -----------------------------------------------------------------------------
# Network Resource Outputs
# -----------------------------------------------------------------------------
output "aca_subnet_id" {
  value = module.network.aca_subnet_id
}