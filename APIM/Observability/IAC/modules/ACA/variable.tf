variable "location" {
  description = "Azure region for the ACA environment and network"
  type        = string
}

variable "resourcegroup" {
  description = "Resource group for ACA resources"
  type        = string
}

variable "prefix" {
  description = "Suffix shared by this demo's resource names"
  type        = string
}

variable "tags" {
  description = "Tags to add to ACA resources"
  type        = map(string)
}

variable "redis_image" {
  description = "Redis 8 image with bundled RedisJSON and RediSearch libraries"
  type        = string
}

variable "vnet_address_prefix" {
  description = "Address space for the shared ACA and APIM virtual network"
  type        = string
}

variable "infrastructure_subnet_prefix" {
  description = "Dedicated, delegated ACA infrastructure subnet"
  type        = string
}

variable "apim_subnet_prefix" {
  description = "Separate, non-delegated subnet for API Management"
  type        = string
}