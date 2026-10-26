# Default variables 
variable "resourcegroup" {
  description = "value for resourcegroup"
  type        = string
  default     = "rg_tf_langchain_demo"
}
variable "location" {
  description = "value for location"
  type        = string
  default     = "swedencentral" # italynorth
}
variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default = {
    owner           = "Ore"
    environment     = "Dev"
    workshop        = "Langchain"
    SecurityControl = "Ignore"
  }
}
variable "prefix" {
  description = "Prefix for all resources in this project"
  type        = string
  default     = "82"
}
variable "environment" {
  description = "Environment name (e.g., dev, test, prod)"
  type        = string
  default     = "dev"
}
variable "foundry_name" {
  description = "Name of the Foundry resource"
  type        = string
  default     = "tf-foundry-orea629a1"
}
variable "foundry_project_name" {
  description = "Name of the Foundry project"
  type        = string
  default     = "tf-foundry-project-orea629a1"
}
variable "custom_subdomain_name" {
  description = "Custom subdomain name for the Foundry project"
  type        = string
  default     = "foundry-orea629a1"
}
variable "cosmos_name" {
  description = "Name of the Cosmos DB account"
  type        = string
  default     = "cosmosdbagentmemorea629a1"
}
variable "cosmos_kind" {
  description = "Kind of the Cosmos DB account"
  type        = string
  default     = "GlobalDocumentDB"
}

variable "cosmos_offer_type" {
  description = "Offer type of the Cosmos DB account"
  type        = string
  default     = "Standard"
}

variable "plan_name" {
  description = "Name of the App Service plan"
  type        = string
  default     = "app-service-plan-mcp-server"
}

variable "appservice_name" {
  description = "Name of the App Service"
  type        = string
  default     = "mcp-open-web-search-orea629a1"
}

variable "os_type" {
  description = "Operating system type for the App Service (e.g., Linux, Windows)"
  type        = string
  default     = "Linux"
}

variable "sku_kind" {
  description = "SKU kind of the App Service plan"
  type        = string
  default     = "B1"
}

variable "environment_name" {
  description = "Environment name (e.g., dev, test, prod)"
  type        = string
  default     = "aca-environment"
}
variable "aca_gemma_name" {
  description = "Name of the Azure Container Apps environment"
  type        = string
  default     = "gemma-4-31b-it-a100"
}
variable "aca_open_webui_name" {
  description = "Name of the Azure Container Apps open web UI"
  type        = string
  default     = "open-webui"
}
variable "aca_qwen_name" {
  description = "Name of the Azure Container Apps Qwen"
  type        = string
  default     = "qwen-3-6-35b-a100"
}

variable "aca_session_pool_shell" {
  description = "Name of the Azure Container Apps session pool for shell"
  type        = string
  default     = "aca-sessionpool-shell-400"
}

variable "aca_session_pool_python" {
  description = "Name of the Azure Container Apps session pool for Python"
  type        = string
  default     = "aca-sessionpool-python-400"
}
variable "vnet_name" {
  description = "Name of the virtual network"
  type        = string
  default     = "vnet-aca"
}

variable "subnet_name" {
  description = "Name of the subnet in the virtual network"
  type        = string
  default     = "snet-aca"
}