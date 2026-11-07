variable "location" {
  description = "Azure region for monitoring resources"
  type        = string
}

variable "resourcegroup" {
  description = "Resource group shared with APIM"
  type        = string
}

variable "prefix" {
  description = "Suffix for the APIM logger name"
  type        = string
}

variable "tags" {
  description = "Tags for monitoring resources"
  type        = map(string)
}

variable "app_insights_name" {
  description = "Name of the workspace-based Application Insights instance"
  type        = string
}

variable "log_analytics_name" {
  description = "Name of the shared observability Log Analytics workspace"
  type        = string
}

variable "retention_in_days" {
  description = "Retention for Application Insights and Log Analytics"
  type        = number

  validation {
    condition     = contains([30, 60, 90, 120, 180, 270, 365, 550, 730], var.retention_in_days)
    error_message = "Retention must be a supported Application Insights value: 30, 60, 90, 120, 180, 270, 365, 550, or 730."
  }
}

variable "apim_sampling_percentage" {
  description = "APIM request telemetry sampling percentage; errors are always logged"
  type        = number

  validation {
    condition     = var.apim_sampling_percentage >= 0 && var.apim_sampling_percentage <= 100
    error_message = "APIM sampling must be between 0 and 100."
  }
}

variable "apim_id" {
  description = "APIM resource ID for platform diagnostics"
  type        = string
}

variable "apim_name" {
  description = "APIM instance name for the Application Insights logger"
  type        = string
}

variable "apim_api_id" {
  description = "APIM API resource ID for API-level telemetry"
  type        = string
}

variable "apim_principal_id" {
  description = "Object ID of APIM's system-assigned managed identity"
  type        = string
}