# Default variables 
variable "resourcegroup" {
  description = "value for resourcegroup"
  type        = string
  default     = "rg-tf-apim-genai-openai-${var.prefix}"
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
  default     = "apim-genai-${var.prefix}"
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
  default     = "foundry-ai-services-${var.prefix}"
}
variable "foundry_custom_subdomain" {
  description = "Custom subdomain name for the Foundry AI Services instance"
  type        = string
  default     = "openai-${var.prefix}"
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