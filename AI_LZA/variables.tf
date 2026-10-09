# Default variables 

variable "subscription_id" {
  description = "Azure Subscription ID for the deployment"
  type        = string
  default     = "f76acfa2-f79b-465f-a4ef-4cd279b35d4d"
}

variable "environment_name" {
  description = "Environment name used for resource naming (e.g., citadel-dev, citadel-prod)"
  type        = string
  default     = "citadel-dev"

  validation {
    condition     = can(regex("^[a-z0-9-]{3,24}$", var.environment_name))
    error_message = "Environment name must be 3-24 lowercase alphanumeric characters or hyphens."
  }
}

variable "location" {
  description = "Primary Azure region for deployment"
  type        = string
  default     = "swedencentral"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {
    owner       = "Ore"
    environment = "AI LZ Terraform"
  }
}

variable "purge_soft_delete_on_destroy" {
  description = "If true, purge soft-deleted resources on destroy"
  type        = bool
  default     = false
}

variable "resource_group_name" {
  description = "Resource group name. Leave empty for auto-generated."
  type        = string
  default     = "tf_ai_lz"
}

variable "apim_service_name" {
  description = "API Management service name. Leave empty for auto-generated."
  type        = string
  default     = "apim"
}

variable "cosmos_db_account_name" {
  description = "Cosmos DB account name. Leave empty for auto-generated."
  type        = string
  default     = ""
}

variable "eventhub_namespace_name" {
  description = "Event Hub namespace name. Leave empty for auto-generated."
  type        = string
  default     = ""
}

variable "log_analytics_name" {
  description = "Log Analytics workspace name. Leave empty for auto-generated."
  type        = string
  default     = ""
}

variable "key_vault_name" {
  description = "Key Vault name. Leave empty for auto-generated."
  type        = string
  default     = ""
}
# -----------------------------------------------------------------------------
# SECURITY/KEY-VAULT MODULE CONFIGURATION
# -----------------------------------------------------------------------------
variable "soft_delete_retention_days" {
  description = "Number of days to retain soft-deleted Key Vaults (1-90, default 7)"
  type        = number
  default     = 7

  validation {
    condition     = var.soft_delete_retention_days >= 1 && var.soft_delete_retention_days <= 90
    error_message = "Soft delete retention must be between 1 and 90 days."
  }
}

variable "purge_protection_enabled" {
  description = "Enable purge protection on Key Vault (prevents permanent deletion)"
  type        = bool
  default     = true
  
}

variable "rbac_authorization_enabled" {
  description = "Enable RBAC authorization on Key Vault"
  type        = bool
  default     = true
}

variable "network_acl_default_action" {
  description = "Default network access action for Key Vault (Allow or Deny)"
  type        = string
  default     = "Deny"

  validation {
    condition     = contains(["Allow", "Deny"], var.network_acl_default_action)
    error_message = "Default action must be Allow or Deny."
  }
}

variable "kv_public_network_access_enabled" {
  description = "Enable public network access to Key Vault (true or false)"
  type        = bool
  default     = false
}

# -----------------------------------------------------------------------------
# NETWORKING
# -----------------------------------------------------------------------------

variable "use_existing_vnet" {
  description = "Use an existing VNet instead of creating a new one"
  type        = bool
  default     = false
}

variable "existing_vnet_rg" {
  description = "Resource group of the existing VNet (required if use_existing_vnet = true)"
  type        = string
  default     = ""
}

variable "vnet_name" {
  description = "VNet name (existing or new)"
  type        = string
  default     = ""
}

variable "vnet_address_prefix" {
  description = "Address prefix for new VNet"
  type        = string
  default     = "10.170.0.0/24"
}

variable "apim_subnet_name" {
  description = "APIM subnet name"
  type        = string
  default     = "snet-citadel-apim"
}

variable "apim_subnet_prefix" {
  description = "APIM subnet address prefix (for new VNet)"
  type        = string
  default     = "10.170.0.0/26"
}

variable "private_endpoint_subnet_name" {
  description = "Private endpoint subnet name"
  type        = string
  default     = "snet-citadel-pe"
}

variable "private_endpoint_subnet_prefix" {
  description = "Private endpoint subnet address prefix (for new VNet)"
  type        = string
  default     = "10.170.0.64/26"
}

variable "logic_app_subnet_name" {
  description = "Logic App / Function App subnet name"
  type        = string
  default     = "snet-citadel-functions"
}

variable "logic_app_subnet_prefix" {
  description = "Logic App subnet address prefix (for new VNet)"
  type        = string
  default     = "10.170.0.128/26"
}

variable "enable_agent_subnet" {
  type    = bool
  default = true
}
variable "agent_subnet_name" {
  type    = string
  default = "snet-agents"
}
variable "agent_subnet_prefix" {
  type    = string
  default = "10.170.0.192/26"
}

variable "apim_network_type" {
  description = "APIM network type: 'External', 'Internal', or 'None'"
  type        = string
  default     = "External"

  validation {
    condition     = contains(["External", "Internal", "None"], var.apim_network_type)
    error_message = "Must be External, Internal, or None."
  }
}

variable "apim_v2_use_private_endpoint" {
  description = "Enable private endpoint for APIM V2 SKUs"
  type        = bool
  default     = true
}

variable "apim_v2_public_network_access" {
  description = "Allow public access for APIM V2 SKUs"
  type        = bool
  default     = true
}

# DNS Configuration
variable "dns_zone_rg" {
  description = "Resource group containing existing Private DNS Zones"
  type        = string
  default     = ""
}

variable "dns_subscription_id" {
  description = "Subscription ID containing existing Private DNS Zones"
  type        = string
  default     = ""
}

variable "existing_private_dns_zones" {
  description = "Map of existing private DNS zone resource IDs"
  type        = map(string)
  default     = {}
}

# -----------------------------------------------------------------------------
# COMPUTE SKU & SIZING
# -----------------------------------------------------------------------------

variable "apim_sku" {
  description = <<-EOT
    APIM SKU: Developer, StandardV2, Premium, PremiumV2.

    REGION AVAILABILITY (important — v2 SKUs are NOT globally available):

      - Developer / Premium (classic):
          Globally available in virtually all Azure public regions.

      - StandardV2 / PremiumV2 (stv2 platform):
          Available in a limited subset of regions. 
          Authoritative list (check before deploy):
          https://learn.microsoft.com/azure/api-management/api-management-region-availability
          az apim list-skus --location <region>

    If you hit `SkuNotSupportedInRegion` at apply time, either:
      (a) pick a supported region for `location`, or
      (b) fall back to `Premium` (classic)
  EOT
  type        = string
  default     = "StandardV2"

  validation {
    condition     = contains(["Developer", "StandardV2", "Premium", "PremiumV2"], var.apim_sku)
    error_message = "Must be Developer, StandardV2, Premium, or PremiumV2."
  }
}

variable "apim_sku_units" {
  description = "Number of APIM scale units"
  type        = number
  default     = 1
}

variable "apim_publisher_email" {
  description = "APIM publisher email"
  type        = string
  default     = "admin@contoso.com"
}

variable "apim_publisher_name" {
  description = "APIM publisher name"
  type        = string
  default     = "AI Citadel Admin"
}

variable "cosmos_db_rus" {
  description = "Cosmos DB provisioned throughput (RU/s)"
  type        = number
  default     = 400
}

variable "eventhub_capacity_units" {
  description = "Event Hub capacity units"
  type        = number
  default     = 1
}

variable "eventhub_partition_count" {
  description = "Event Hub partition count"
  type        = number
  default     = 4
}

variable "eventhub_disaster_recovery_config" {
  description = <<-EOT
    Optional disaster recovery pairing for the Event Hub namespace (Bicep
    parity: `disasterRecoveryConfig`). Set to `null` to skip. When provided,
    pairs this namespace with a partner namespace under the given alias.
    The partner namespace must already exist and match SKU tier.
  EOT
  type = object({
    partner_namespace_id = string
    alias                = optional(string, "default")
  })
  default = null
}

variable "logic_app_sku_tier" {
  description = "Logic App (Standard) SKU tier"
  type        = string
  default     = "WorkflowStandard"
}

variable "logic_app_sku_size" {
  description = "Logic App (Standard) SKU size"
  type        = string
  default     = "WS1"
}

variable "language_service_sku" {
  description = "Azure Language Service SKU"
  type        = string
  default     = "S"
}

variable "content_safety_sku" {
  description = "Azure Content Safety SKU"
  type        = string
  default     = "S0"
}

variable "api_center_sku" {
  description = "SKU for API Center service. Free tier is 'Free', paid tier is 'Standard'."
  type        = string
  default     = "Free"

  validation {
    condition     = contains(["Free", "Standard"], var.api_center_sku)
    error_message = "SKU must be 'Free' or 'Standard'."
  }
}

variable "key_vault_sku" {
  description = "Key Vault SKU"
  type        = string
  default     = "standard"
}

# -----------------------------------------------------------------------------
# FEATURE FLAGS
# -----------------------------------------------------------------------------

variable "enable_api_center" {
  description = "Deploy API Center as AI Registry"
  type        = bool
  default     = true
}

variable "enable_pii_redaction" {
  description = "Enable PII detection and masking via Language Service"
  type        = bool
  default     = true
}

variable "enable_content_safety" {
  description = "Enable Azure AI Content Safety"
  type        = bool
  default     = true
}

variable "enable_redis_cache" {
  description = "Deploy Azure Managed Redis for semantic caching"
  type        = bool
  default     = false
}

variable "create_app_insights_dashboards" {
  description = "Create Application Insights dashboards"
  type        = bool
  default     = true
}

# -----------------------------------------------------------------------------
# LOG ANALYTICS STRATEGY
# -----------------------------------------------------------------------------

variable "use_existing_log_analytics" {
  description = "Use an existing Log Analytics workspace"
  type        = bool
  default     = false
}

variable "existing_log_analytics_id" {
  description = "Resource ID of existing Log Analytics workspace"
  type        = string
  default     = ""
}

variable "existing_log_analytics_subscription_id" {
  description = "Subscription ID of the BYO Log Analytics workspace when it lives in a different subscription than the deployment. Leave blank to default to var.subscription_id. Bicep parity: existingLogAnalyticsSubscriptionId."
  type        = string
  default     = ""
}

# -----------------------------------------------------------------------------
# NETWORK ACCESS SETTINGS
# -----------------------------------------------------------------------------

variable "cosmos_db_public_access" {
  description = "Cosmos DB public network access: Enabled or Disabled"
  type        = string
  default     = "Disabled"
}

variable "eventhub_network_access" {
  description = "Event Hub public network access: Enabled or Disabled"
  type        = string
  default     = "Enabled"
}

variable "ai_foundry_external_access" {
  description = "AI Foundry external network access"
  type        = bool
  default     = false
}

# -----------------------------------------------------------------------------
# ENTRA ID AUTHENTICATION
# -----------------------------------------------------------------------------

variable "entra_auth_enabled" {
  description = "Enable Entra ID JWT validation on APIM"
  type        = bool
  default     = false
}

variable "entra_tenant_id" {
  description = "Entra ID tenant ID for JWT validation"
  type        = string
  default     = ""
}

variable "entra_client_id" {
  description = "Entra ID client ID (application ID)"
  type        = string
  default     = ""
}

variable "entra_audience" {
  description = "Entra ID audience (resource identifier)"
  type        = string
  default     = ""
}

# -----------------------------------------------------------------------------
# AI FOUNDRY CONFIGURATION
# -----------------------------------------------------------------------------

variable "foundry_network_injection_enabled" {
  type    = bool
  default = true
}

variable "ai_foundry_instances" {
  description = "List of AI Foundry instances to deploy"
  type = list(object({
    name                 = optional(string, "")
    location             = string
    custom_subdomain     = optional(string, "")
    default_project_name = optional(string, "citadel-governance-project")
    network_injection_enabled = optional(bool, true)
  }))
  default = [
    {
      location             = "swedencentral"
      default_project_name = "citadel-governance-project"
    }
  ]
}

variable "ai_foundry_models" {
  description = "List of models to deploy across AI Foundry instances"
  type = list(object({
    name              = string
    publisher         = optional(string, "OpenAI")
    version           = string
    sku               = optional(string, "GlobalStandard")
    capacity          = optional(number, 100)
    ai_service_index  = optional(number, 0)
  }))
  default = [
    {
      name    = "gpt-4o"
      version = "2024-11-20"
    },
    {
      name     = "gpt-4o-mini"
      version  = "2024-07-18"
    }
  ]
}

# -----------------------------------------------------------------------------
# LLM BACKEND CONFIGURATION
# -----------------------------------------------------------------------------

variable "llm_backend_config" {
  description = <<-EOT
    OPTIONAL — full override of APIM LLM backend configuration.

    Leave as `[]` (the default) to let the root module auto-derive backends
    from `enable_ai_foundry` + `ai_foundry_instances` + `ai_foundry_models`.
    One backend is created per Foundry instance, priority 1 for instance 0,
    priority 2 for subsequent instances; models are grouped by
    `ai_service_index`.

    Populate this variable ONLY when you need non-Foundry backends
    exclusively (e.g. external Azure OpenAI, third-party LLM gateway). When
    non-empty, it REPLACES the auto-derived list entirely.

    To keep auto-derivation AND add external backends, leave this empty and
    use `extra_llm_backends` instead.

    Each `supported_models` entry is an object (mirrors Bicep).
  EOT
  type = list(object({
    backend_id   = string
    backend_type = string # ai-foundry, azure-openai, external
    endpoint     = string
    auth_scheme  = string # managedIdentity, apiKey, token
    auth_type    = optional(string)  # 'managed-identity'|'aws-sigv4'|'api-key-bearer'|'api-key-header'|'none'
    auth_config  = optional(object({
      named_value_key = optional(string)
    }))
    supported_models = list(object({
      name                = string
      sku                 = optional(string, "Standard")
      capacity            = optional(number, 100)
      modelFormat         = optional(string, "OpenAI")
      modelVersion        = optional(string, "1")
      apiVersion          = optional(string, "2024-02-15-preview")
      timeout             = optional(number, 120)
      inferenceApiVersion = optional(string, "")
      retirementDate      = optional(string, "")
    }))
    priority = optional(number, 1)
    weight   = optional(number, 100)
  }))
  default = []
}

variable "extra_llm_backends" {
  description = <<-EOT
    OPTIONAL — APPENDED to the auto-derived Foundry backends.

    Use to mix Foundry (auto-derived) with external backends (Azure OpenAI
    outside Foundry, third-party endpoints, etc.) in the same gateway without
    losing auto-derivation. Same object shape as `llm_backend_config`.

    Ignored when `llm_backend_config` is set (full override takes precedence).
  EOT
  type = list(object({
    backend_id   = string
    backend_type = string
    endpoint     = string
    auth_scheme  = string # managedIdentity, apiKey, token
    auth_type    = optional(string)  # 'managed-identity'|'aws-sigv4'|'api-key-bearer'|'api-key-header'|'none'
    auth_config  = optional(object({
      named_value_key = optional(string)
    }))
    supported_models = list(object({
      name                = string
      sku                 = optional(string, "Standard")
      capacity            = optional(number, 100)
      modelFormat         = optional(string, "OpenAI")
      modelVersion        = optional(string, "1")
      apiVersion          = optional(string, "2024-02-15-preview")
      timeout             = optional(number, 120)
      inferenceApiVersion = optional(string, "")
      retirementDate      = optional(string, "")
    }))
    priority = optional(number, 1)
    weight   = optional(number, 100)
  }))
  default = []
}

# -----------------------------------------------------------------------------
# DIAGNOSTIC LOGGING
# -----------------------------------------------------------------------------

variable "apim_log_verbosity" {
  description = "APIM diagnostic log verbosity: verbose, information, error"
  type        = string
  default     = "information"
}

variable "apim_log_body_bytes" {
  description = "Max bytes to log from request/response body"
  type        = number
  default     = 8192
}
