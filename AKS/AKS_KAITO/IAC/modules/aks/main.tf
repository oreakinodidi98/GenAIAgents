# get latest azure AKS latest Version
data "azurerm_kubernetes_service_versions" "versions" {
    location = var.location
    include_preview = false
}
data "azurerm_subscription" "current" {}
#create managed identity
resource "azurerm_user_assigned_identity" "aks_cluster" {
  name                = var.identity_prefix
  location            = var.location
  resource_group_name = var.resourcegroup
}
#create role assighnment at RG scope with managed identity
resource "azurerm_role_assignment" "role_rg" {
  scope                = var.resourcegroup_id
  role_definition_name = "Network Contributor"
  principal_id         = azurerm_user_assigned_identity.aks_cluster.principal_id
}
# create role assignment at subscription scope with managed identity
resource "azurerm_role_assignment" "contributor_role_assignment" {
  scope                = data.azurerm_subscription.current.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.aks_cluster.principal_id
}
#create acr
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = var.resourcegroup
  location            = var.location
  sku                 = "Standard"
  admin_enabled       = false
}

#create role assignment for acr pull with managed identity
resource "azurerm_role_assignment" "mi_role_acrpull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.aks_cluster.principal_id
  skip_service_principal_aad_check = true
}
# Role Assignment for AKS Key Vault Secrets Provider identity
resource "azurerm_role_assignment" "aks_kv_secrets_user" {
  #scope                = azurerm_key_vault.main.id
  scope                = var.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_kubernetes_cluster.aks_cluster.key_vault_secrets_provider[0].secret_identity[0].object_id
}
# create AKS cluster
resource "azurerm_kubernetes_cluster" "aks_cluster" {
  name                = var.aks_cluster_name
  location            = var.location
  resource_group_name = var.resourcegroup
  dns_prefix          = replace("${var.resourcegroup}-cluster", "_", "-")
  kubernetes_version = data.azurerm_kubernetes_service_versions.versions.latest_version
  node_resource_group = "${var.resourcegroup}-node-rg"
  # OIDC and Workload Identity
  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  default_node_pool {
    name       = "systempool"
    temporary_name_for_rotation = "systemnptmp"
    node_count                  = var.system_node_count
    vm_size                     = "Standard_D2ads_v6"
    os_disk_size_gb             = 64
    os_disk_type                = "Ephemeral" # "Managed"
    ultra_ssd_enabled           = false
    os_sku                      = "Ubuntu" # Ubuntu, AzureLinux, Windows2019, Windows2022

    upgrade_settings {
      drain_timeout_in_minutes      = 10
      max_surge                     = "10%"
      node_soak_duration_in_minutes = 1
      undrainable_node_behavior     = "Cordon" # "Schedule"
    }

  }
identity {
    type = "SystemAssigned"
  }
  # Monitoring addon
  oms_agent {
    log_analytics_workspace_id = var.log_analytics_id
  }
  tags = {
      "nodepool" = "system"
      "env"      = "AKS-Clasic"
  }

  # Key Vault Secrets Provider addon
  key_vault_secrets_provider {
    secret_rotation_enabled = true
  }

  # Web Application Routing addon (creates app-routing-system namespace + nginx ingress)
  web_app_routing {
    dns_zone_ids = []
  }

  # Azure Monitor for containers
  monitor_metrics {
    annotations_allowed = null
    labels_allowed      = null
  }
  # Linux profile for the AKS nodes
  linux_profile {
    admin_username = "ubuntu"
    ssh_key {
      key_data = file(var.ssh_public_key)
    }
  }
  # Network profile for the AKS cluster
  network_profile {
        network_plugin = "azure" # "kubenet", "azure", "none"
        network_plugin_mode = "overlay"
        network_policy      = "cilium" # calico, azure and cilium
        network_data_plane  = "cilium" # azure and cilium
        # load_balancer_sku   = "standard"
        # pod_cidr            = "10.244.0.0/16"
        # service_cidr        = "172.16.0.0/16"
        # dns_service_ip      = "172.16.0.10"
    }
  # Lifecycle settings for the AKS cluster
  lifecycle {
    ignore_changes = [
      default_node_pool[0].node_count,
    ]
  }
}

# # Enable ACNS features using AzAPI (for features not yet in AzureRM)
# resource "azapi_update_resource" "aks_acns" {
#   type        = "Microsoft.ContainerService/managedClusters@2024-05-01"
#   resource_id = azurerm_kubernetes_cluster.aks_cluster.id

#   body = jsonencode({
#     properties = {
#       networkProfile = {
#         advancedNetworking = {
#           enabled = true
#           observability = {
#             enabled = true
#           }
#           security = {
#             fqdnPolicy = {
#               enabled = true
#             }
#           }
#         }
#       }
#     }
#   })

#   depends_on = [azurerm_kubernetes_cluster.aks_cluster]
# }

# User Node Pool
resource "azurerm_kubernetes_cluster_node_pool" "user" {
  name                  = "userpool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks_cluster.id
  vm_size               = "Standard_A2_v2"
  node_count            = 1
  mode                  = "User"
  os_sku                = "AzureLinux"

  depends_on = [azapi_update_resource.aks_acns]
}

# aks_nodepool_gpu_NC24ads_A100_v4
resource "azurerm_kubernetes_cluster_node_pool" "nc24ads_a100_v4" {
  name                        = "nc24adsa100"
  temporary_name_for_rotation = "nc24adsa100t"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks_cluster.id
  mode                        = "User"
  vm_size               = var.node_pool_gpu_vm_size
  node_count                  = 1
  auto_scaling_enabled        = true
  min_count                   = 1
  max_count                   = 1
  gpu_driver                  = "Install" # "Install" or "None"
  os_type                     = "Linux"
  zones                       = []
  os_disk_size_gb             = 64 # 1024 # 960 # 512
  os_disk_type                = "Ephemeral" # "Managed" 
  priority                    = "Spot"
  eviction_policy             = "Delete"
  node_labels = {
    "kubernetes.azure.com/scalesetpriority" = "spot"
    "apps"                                  = "phi-4"
  }

  node_taints = [
    "kubernetes.azure.com/scalesetpriority=spot:NoSchedule",
  ]

  tags = {
    EnableManagedGPUExperience = true # enables managed GPU experience for the node pool, which includes automatic installation and management of GPU drivers and monitoring of GPU health and performance
  }
  # depends_on = [azapi_update_resource.k8s-default-node-pool-systempool-taint]
}

# new versions here: https://github.com/kaito-project/kaito/releases
locals {
  kaito_workspace_version = "0.10.0" # "0.9.1"
  kaito_ragengine_version = "0.10.0" # "0.9.1"
}

resource "terraform_data" "helm_repo_update" {
  triggers_replace = [
    azurerm_kubernetes_cluster.aks_cluster.id
  ]

  provisioner "local-exec" {
    # interpreter = ["PowerShell", "-Command"]
    command = <<-EOT
      helm repo update
    EOT
  }
}

# Install the kaito-workspace chart
resource "helm_release" "kaito_workspace" {
  name             = "kaito-workspace"
  chart            = "https://raw.githubusercontent.com/kaito-project/kaito/refs/heads/gh-pages/charts/kaito/workspace-${local.kaito_workspace_version}.tgz"
  namespace        = "kaito-workspace"
  create_namespace = true
  # upgrade_install  = true

  set = [
    {
      name  = "clusterName"
      value = azurerm_kubernetes_cluster.aks_cluster.name
    },
    {
      name  = "defaultNodeImageFamily"
      value = "ubuntu"
    },
    {
      name  = "featureGates.gatewayAPIInferenceExtension"
      value = "true"
    },
    {
      name  = "featureGates.disableNodeAutoProvisioning"
      value = "false"
    },
    {
      name  = "gpu-feature-discovery.nfd.enabled"
      value = "true"
    },
    {
      name  = "gpu-feature-discovery.gfd.enabled"
      value = "true"
    },
    {
      name  = "nvidiaDevicePlugin.enabled"
      value = "true"
    }
  ]

  depends_on = [
    azurerm_kubernetes_cluster_node_pool.nc24ads_a100_v4,
    terraform_data.helm_repo_update
  ]
}

# Install the kaito-ragengine chart
resource "helm_release" "kaito_ragengine" {
  name             = "kaito-ragengine"
  chart            = "https://raw.githubusercontent.com/kaito-project/kaito/refs/heads/gh-pages/charts/kaito/ragengine-${local.kaito_ragengine_version}.tgz"
  namespace        = "kaito-ragengine"
  create_namespace = true
  # upgrade_install  = true

  depends_on = [
    azurerm_kubernetes_cluster_node_pool.nc24ads_a100_v4,
    terraform_data.helm_repo_update
  ]
}