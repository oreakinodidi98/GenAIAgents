variable "location" {
  description = "Azure region for the Managed Redis instance"
  type        = string
}

variable "resourcegroup" {
  description = "Resource group for the Managed Redis instance"
  type        = string
}

variable "tags" {
  description = "Tags to add to the Managed Redis instance"
  type        = map(string)
}

variable "redis_name" {
  description = "Name of the Managed Redis instance"
  type        = string
}

variable "redis_sku_name" {
  description = "SKU name for the Managed Redis instance"
  type        = string
}