# Default variables 
variable "resourcegroup" {
  description = "value for resourcegroup"
  type        = string
  default     = null
}
variable "location" {
  description = "value for location"
  type        = string
  default     = "UK South"
}
variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default = {
    owner       = "Ore"
    environment = "APIM"
  }
}
variable "environment" {
  description = "Environment name (e.g., dev, test, prod)"
  type        = string
  default     = "dev"
}
variable "prefix" {
  description = "Prefix to be used for all resources in this example"
  type        = string
  default     = "320"
}
variable "apim_name" {
  description = "Name of the API Management instance"
  type        = string
  default     = null
}
variable "apim_sub_name" {
  description = "Name of the API Management subscription for OpenAI"
  type        = string
  default     = "apim-api-subscription-openai"
}
variable "apim_api_name" {
  description = "Name of the API Management API for OpenAI"
  type        = string
  default     = "apim-api-openai"
}
variable "apim_publisher_name" {
  description = "Publisher name for the API Management instance"
  type        = string
  default     = "My Company"
}

variable "apim_publisher_email" {
  description = "Publisher email for the API Management instance"
  type        = string
  default     = "noreply@mycompany.com"
}
variable "apim_sku_name" {
  description = "SKU name for the API Management instance"
  type        = string
  default     = "Developer_1" # "Consumption_0" # "Developer_1"
}
variable "foundry_name" {
  description = "Name of the Foundry AI Services instance"
  type        = string
  default     = null
}
variable "foundry_custom_subdomain" {
  description = "Custom subdomain name for the Foundry AI Services instance"
  type        = string
  default     = null
}
variable "foundry_sku_name" {
  description = "SKU name for the Foundry AI Services instance"
  type        = string
  default     = "S0"
}
variable "foundry_cognitive_deployment_name" {
  description = "Name of the cognitive deployment for the Foundry AI Services instance"
  type        = string
  default     = "gpt-4o"
}
variable "foundry_cognitive_deployment_sku_name" {
  description = "SKU name for the cognitive deployment of the Foundry AI Services instance"
  type        = string
  default     = "GlobalStandard" # "Standard" # DataZoneStandard, GlobalBatch, GlobalStandard and ProvisionedManaged
}
variable "foundry_cognitive_deployment_capacity" {
  description = "Capacity for the cognitive deployment of the Foundry AI Services instance"
  type        = number
  default     = 20
}
variable "foundry_cognitive_deployment_model_format" {
  description = "Model format for the cognitive deployment of the Foundry AI Services instance"
  type        = string
  default     = "OpenAI"
}

variable "foundry_cognitive_deployment_model_name" {
  description = "Model name for the cognitive deployment of the Foundry AI Services instance"
  type        = string
  default     = "gpt-4o"
}

variable "foundry_cognitive_deployment_model_description" {
  description = "Description for the cognitive deployment model of the Foundry AI Services instance"
  type        = string
  default     = "Cognitive deployment model for Foundry AI Services"
}

variable "foundry_cognitive_deployment_model_version" {
  description = "Version for the cognitive deployment model of the Foundry AI Services instance"
  type        = string
  default     = "2024-11-20"
}

variable "redis_name" {
  description = "Name of the Managed Redis instance; defaults to redis-<prefix>"
  type        = string
  default     = null
}

variable "redis_sku_name" {
  description = "SKU name for the Managed Redis instance"
  type        = string
  default     = "Balanced_B0"
}

variable "foundry_embedding_deployment_name" {
  description = "Name of the embeddings deployment used by semantic caching"
  type        = string
  default     = "text-embedding-3-small"
}

variable "foundry_embedding_model_name" {
  description = "OpenAI embeddings model name"
  type        = string
  default     = "text-embedding-3-small"
}

variable "foundry_embedding_model_version" {
  description = "Version of the OpenAI embeddings model"
  type        = string
  default     = "1"
}

variable "foundry_embedding_sku_name" {
  description = "SKU for the embeddings deployment; confirm regional availability"
  type        = string
  default     = "Standard"
}

variable "foundry_embedding_capacity" {
  description = "Capacity units for the embeddings deployment"
  type        = number
  default     = 10
}

variable "cache_backend" {
  description = "Semantic-cache backend: managed_redis or aca"
  type        = string
  default     = "managed_redis"

  validation {
    condition     = contains(["managed_redis", "aca"], var.cache_backend)
    error_message = "cache_backend must be managed_redis or aca."
  }
}

variable "aca_redis_image" {
  description = "Redis 8 image with bundled search modules for the ACA cache"
  type        = string
  default     = "redis:8.2.3"
}

variable "aca_vnet_address_prefix" {
  description = "Address space for the ACA/APIM VNet; avoid overlaps with connected networks"
  type        = string
  default     = "10.0.0.0/16"
}

variable "aca_infrastructure_subnet_prefix" {
  description = "Dedicated ACA infrastructure subnet within the VNet"
  type        = string
  default     = "10.0.0.0/23"
}

variable "aca_apim_subnet_prefix" {
  description = "Non-delegated APIM subnet within the VNet"
  type        = string
  default     = "10.0.2.0/24"
}

variable "app_insights_name" {
  description = "Application Insights name; defaults to app-insights-<prefix>"
  type        = string
  default     = null
}

variable "log_analytics_name" {
  description = "Log Analytics name; defaults to log-observability-<prefix>"
  type        = string
  default     = null
}

variable "observability_retention_in_days" {
  description = "Retention for Application Insights and its Log Analytics workspace"
  type        = number
  default     = 30
}

variable "apim_sampling_percentage" {
  description = "Percentage of APIM requests logged to Application Insights"
  type        = number
  default     = 100
}

variable "grafana_name" {
  description = "Managed Grafana name; defaults to grafana-<prefix>"
  type        = string
  default     = null
}

variable "grafana_major_version" {
  description = "Managed Grafana major version (11 or 12)"
  type        = string
  default     = "11"
}

variable "grafana_admin_object_id" {
  description = "Grafana administrator Entra object ID; defaults to the Terraform caller"
  type        = string
  default     = null
}