terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
    azapi = {
      source = "azure/azapi"
    }
  }
}

data "azurerm_client_config" "current" {}

resource "azurerm_container_app_environment" "aca_environment" {
  name                           = var.environment_name
  location                       = var.location
  resource_group_name            = var.resourcegroup
  public_network_access          = "Enabled"
  logs_destination               = "azure-monitor" # "log-analytics"
  internal_load_balancer_enabled = false
  zone_redundancy_enabled        = false
  infrastructure_subnet_id       = var.aca_subnet_id

  identity {
    type = "SystemAssigned"
  }

  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }

  workload_profile {
    name                  = "profile-D4"
    workload_profile_type = "D4" # D4, D8, D16, D32, E4, E8, E16 and E32.
    minimum_count         = 0
    maximum_count         = 1
  }

  # workload_profile {
  #   name                  = "GPU-NC8as-T4"
  #   workload_profile_type = "Consumption-GPU-NC8as-T4" # D4, D8, D16, D32, E4, E8, E16 and E32.
  #   # minimum_count         = 0
  #   # maximum_count         = 1
  # }

  # workload_profile {
  #   name                  = "GPU-NC24-A100"
  #   workload_profile_type = "Consumption-GPU-NC24-A100" # D4, D8, D16, D32, E4, E8, E16 and E32.
  #   # minimum_count         = 0
  #   # maximum_count         = 1
  # }

  lifecycle {
    ignore_changes = [workload_profile]
  }
}

# There is a bug with adding GPU profiles via terraform, so we need to use local-exec to run the az cli command to add the GPU profiles after the ACA environment is created
resource "terraform_data" "add_serverless_gpu_profile_GPU-NC24-A100" {
  triggers_replace = [azurerm_container_app_environment.aca_environment.id]

  provisioner "local-exec" {
    command = "az containerapp env workload-profile add --name ${azurerm_container_app_environment.aca_environment.name} --resource-group ${azurerm_container_app_environment.aca_environment.resource_group_name} --workload-profile-type Consumption-GPU-NC24-A100 --workload-profile-name GPU-NC24-A100"
  }

  depends_on = [ azurerm_container_app_environment.aca_environment ]
}

# There is a bug with adding GPU profiles via terraform, so we need to use local-exec to run the az cli command to add the GPU profiles after the ACA environment is created
resource "terraform_data" "add_serverless_gpu_profile_GPU-NC8as-T4" {
  triggers_replace = [azurerm_container_app_environment.aca_environment.id]

  provisioner "local-exec" {
    command = "az containerapp env workload-profile add --name ${azurerm_container_app_environment.aca_environment.name} --resource-group ${azurerm_container_app_environment.aca_environment.resource_group_name} --workload-profile-type Consumption-GPU-NC8as-T4 --workload-profile-name GPU-NC8as-T4"
  }

  depends_on = [ azurerm_container_app_environment.aca_environment, terraform_data.add_serverless_gpu_profile_GPU-NC24-A100 ]
}


resource "azurerm_container_app" "aca_gemma4_31b_it_a100" {
  container_app_environment_id = azurerm_container_app_environment.aca_environment.id
  name                         = var.aca_gemma_name
  resource_group_name          = var.resourcegroup
  revision_mode                = "Single"
  workload_profile_name        = "GPU-NC24-A100" # "GPU-NC8as-T4"

  ingress {
    allow_insecure_connections = true
    client_certificate_mode    = "ignore"
    external_enabled           = true
    target_port                = 8000
    transport                  = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas                     = 1
    max_replicas                     = 2
    polling_interval_in_seconds      = 30
    cooldown_period_in_seconds       = 1800
    termination_grace_period_seconds = 30
    revision_suffix                  = ""

    container {
      image  = "vllm/vllm-openai:gemma4-cu130"
      name   = "gemma4-31b-it"
      cpu    = 4      # 24      # 8
      memory = "32Gi" # "16Gi" # "220Gi" # "56Gi"

      # src: https://docs.vllm.ai/projects/recipes/en/latest/Google/Gemma4.html#pip-nvidia-cuda
      args = [
        "--model", "google/gemma-4-31B-it",
        "--tensor-parallel-size", "1",
        "--max-model-len", "32768",
        "--gpu-memory-utilization", "0.85",
        "--limit-mm-per-prompt", jsonencode({ "images" : 4, "videos" : 1, "audios" : 1 }),
        "--enable-auto-tool-choice",
        "--tool-call-parser", "gemma4",
        "--reasoning-parser", "gemma4",
        "--chat-template", "examples/tool_chat_template_gemma4.jinja",
        "--host", "0.0.0.0",
        "--port", "8000"
      ]

      startup_probe {
        path                    = "/health"
        transport               = "HTTP"
        port                    = "8000"
        failure_count_threshold = "4"
        initial_delay           = "60"
        interval_seconds        = "240"
        timeout                 = "240"
      }

      liveness_probe {
        path                    = "/health"
        transport               = "HTTP"
        port                    = "8000"
        failure_count_threshold = "4"
        initial_delay           = "60"
        interval_seconds        = "240"
        timeout                 = "240"
      }

      readiness_probe {
        path                    = "/health"
        transport               = "HTTP"
        port                    = "8000"
        failure_count_threshold = "4"
        initial_delay           = "60"
        interval_seconds        = "240"
        timeout                 = "240"
      }

      # # Optional: HF token if needed for gated models
      # env {
      #   name  = "HF_TOKEN"
      #   value = ""
      # }
    }
    http_scale_rule {
      name                = "http-scale"
      concurrent_requests = 2
    }
  }
}

resource "azurerm_container_app" "open_webui" {
  container_app_environment_id = azurerm_container_app_environment.aca_environment.id
  name                         = var.aca_open_webui_name
  resource_group_name          = var.resourcegroup
  revision_mode                = "Single"
  workload_profile_name        = "Consumption"

  ingress {
    allow_insecure_connections = true
    client_certificate_mode    = "ignore"
    external_enabled           = true
    target_port                = 8080
    transport                  = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas                     = 1
    max_replicas                     = 1
    polling_interval_in_seconds      = 30
    cooldown_period_in_seconds       = 300
    termination_grace_period_seconds = 30

    container {
      image  = "ghcr.io/open-webui/open-webui:main"
      name   = var.aca_open_webui_name
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "ENABLE_OPENAI_API"
        value = "True"
      }
      env {
        name  = "OPENAI_API_BASE_URLS"
        value = "http://${azurerm_container_app.aca_gemma4_31b_it_a100.ingress.0.fqdn}/v1;http://${azurerm_container_app.aca_qwen_36_35b_a100.ingress.0.fqdn}/v1"
      }
      # env {
      #   name  = "OPENAI_API_BASE_URL"
      #   value = "http://${azurerm_container_app.aca_gemma4_31b_it_a100.ingress.0.fqdn}/v1"
      # }
    }
  }
}
resource "azurerm_container_app" "aca_qwen_36_35b_a100" {
  container_app_environment_id = azurerm_container_app_environment.aca_environment.id
  name                         = var.aca_qwen_name
  resource_group_name          = var.resourcegroup
  revision_mode                = "Single"
  workload_profile_name        = "GPU-NC24-A100" # "GPU-NC8as-T4"

  ingress {
    allow_insecure_connections = true
    client_certificate_mode    = "ignore"
    external_enabled           = true
    target_port                = 8000
    transport                  = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas                     = 1
    max_replicas                     = 1
    polling_interval_in_seconds      = 30
    cooldown_period_in_seconds       = 1800 # 300 # 3600 # 
    termination_grace_period_seconds = 30
    revision_suffix                  = ""

    container {
      image  = "vllm/vllm-openai"
      name   = "qwen36-35b-a3b"
      cpu    = 4      # 24      # 8
      memory = "64Gi" # "220Gi" # "56Gi"
      # src: https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3.5.html#docker
      args = [
        "--model", "Qwen/Qwen3.6-35B-A3B",
        "--tensor-parallel-size", "1",
        "--max-model-len", "32768",
        "--gpu-memory-utilization", "0.92",
        "--enable-auto-tool-choice",
        "--tool-call-parser", "qwen3_coder",
        "--reasoning-parser", "qwen3",
        "--max-num-seqs", "200",
        "--host", "0.0.0.0",
        "--port", "8000"
        # "--enable-prefix-caching",
        # "--speculative-config", jsonencode({"method": "mtp", "num_speculative_tokens": 2}),
      ]
      startup_probe {
        path                    = "/health"
        transport               = "HTTP"
        port                    = "8000"
        failure_count_threshold = "4"
        initial_delay           = "60"
        interval_seconds        = "240"
        timeout                 = "240"
      }

      liveness_probe {
        path                    = "/health"
        transport               = "HTTP"
        port                    = "8000"
        failure_count_threshold = "4"
        initial_delay           = "60"
        interval_seconds        = "240"
        timeout                 = "240"
      }

      readiness_probe {
        path                    = "/health"
        transport               = "HTTP"
        port                    = "8000"
        failure_count_threshold = "4"
        initial_delay           = "60"
        interval_seconds        = "240"
        timeout                 = "240"
      }

      # # Optional: HF token if needed for gated models
      # env {
      #   name  = "HF_TOKEN"
      #   value = "hf_....."
      # }
    }

    http_scale_rule {
      name                = "http-scale"
      concurrent_requests = 2
    }
  }

  depends_on = [terraform_data.add_serverless_gpu_profile_GPU-NC24-A100]
}