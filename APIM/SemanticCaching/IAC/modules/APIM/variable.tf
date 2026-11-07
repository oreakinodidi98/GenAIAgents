variable "location" {
}
variable "resourcegroup" {
}
variable "prefix" {
}
variable "tags" {
  type = map(string)
}
variable "apim_name" {
}

variable "apim_publisher_name" {
}

variable "apim_publisher_email" {
}

variable "apim_sku_name" {
}
variable "apim_sub_name" {
}
variable "apim_api_name" {
}
variable "foundry_management_endpoint" {
}
variable "foundry_id" {
}

variable "foundry_embedding_endpoint" {
  description = "URL of the Foundry embeddings deployment, without query parameters"
  type        = string
}

variable "redis_cache_enabled" {
  description = "Whether to register Redis as an external APIM cache"
  type        = bool
  default     = false
}

variable "redis_cache_id" {
  description = "Resource ID of the Managed Redis instance"
  type        = string
  default     = null
}

variable "redis_connection_string" {
  description = "Connection string for the selected external Redis cache"
  type        = string
  sensitive   = true
  default     = null
}

variable "apim_vnet_enabled" {
  description = "Whether to inject Developer/Premium APIM into an external-mode VNet"
  type        = bool
  default     = false
}

variable "apim_subnet_id" {
  description = "Non-delegated subnet for APIM virtual network injection"
  type        = string
  default     = null
}