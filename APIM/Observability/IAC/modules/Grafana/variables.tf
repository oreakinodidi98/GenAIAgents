variable "location" {
  description = "Azure region for Managed Grafana"
  type        = string
}

variable "resourcegroup" {
  description = "Resource group for Managed Grafana"
  type        = string
}

variable "tags" {
  description = "Tags for Managed Grafana"
  type        = map(string)
}

variable "grafana_name" {
  description = "Name of the Managed Grafana instance"
  type        = string
}

variable "grafana_major_version" {
  description = "Supported Managed Grafana major version"
  type        = string

  validation {
    condition     = contains(["11", "12"], var.grafana_major_version)
    error_message = "Grafana major version must be 11 or 12."
  }
}

variable "grafana_admin_object_id" {
  description = "Entra user, group, or service principal object ID to grant Grafana Admin"
  type        = string
}

variable "monitoring_scope_id" {
  description = "Resource group scope that Grafana can read through Azure Monitor"
  type        = string
}