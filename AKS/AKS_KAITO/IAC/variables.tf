# Default variables 
variable "resourcegroup" {
  description = "value for resourcegroup"
  type        = string
  default     = "rg-aks-kaito-${var.prefix}"
}
variable "location" {
  description = "value for location"
  type        = string
  default     = "swedencentral"
}
variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default = {
    owner           = "Ore"
    environment     = "Dev"
    workshop        = "AKS Terraform"
    SecurityControl = "Ignore"
  }
}
variable "environment" {
  description = "Environment name (e.g., dev, test, prod)"
  type        = string
  default     = "dev"
}
variable "prefix" {
  default = "800"
}
#################### KV Variables ####################
variable "kv_name" {
  description = "Name of the Key Vault"
  type        = string
  default     = "tfkeyvault"
}
#################### AKS Variables ####################
variable "aks_cluster_name" {
  type    = string
  default = "aks-terraform-clasic"
}
variable "acr_name" {
  type    = string
  default = "oatfclasic01"
}
variable "system_node_count" {
  description = "The number of system nodes for the AKS cluster"
  type        = number
  default     = 2
}
variable "identity_prefix" {
  description = "Prefix for the managed identity name"
  type        = string
  default     = "aksidentity"
}
variable "ssh_public_key" {
  description = "Path to SSH public key for AKS nodes"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}
variable "node_pool_gpu_vm_size" {
  type        = string
  description = "The size of the Virtual Machine."
  default     = "Standard_NC24ads_A100_v4"
  #default     = "Standard_NC6s_v3"
}
#################### Logs Variables ####################
variable "env_name" {
  description = "Name of Environment"
  type        = string
  default     = "mi-k8sdemo"
}
variable "log_analytics_workspace_sku" {
  description = "The pricing SKU of the Log Analytics workspace."
  default     = "PerGB2018"
}
variable "app_insights_name" {
  description = "Name of the Application Insights"
  type        = string
  default     = "tfappinsightswiz"
}
