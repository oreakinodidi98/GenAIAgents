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
variable "app_insights_app_id" {
  description = "Application Insights App ID for monitoring"
  type        = string
}
variable "application_insights_connection_string" {
  description = "Application Insights connection string for monitoring"
  type        = string
}