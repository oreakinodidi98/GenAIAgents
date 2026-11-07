# Observability

focus on getting logs and metrics from LLM models
These metrics provide info around user, remaining tokens per user or application, cost about models
charge back for teams (if model is shared by multiple teams)
New policy for emit token metric

App -> APIM (policy for metrics)-> Application insight
can then run queryies using KQL to get more insight and data

To create infrasturcture check IAC
or create APIM
creat foundry
assighn cognitive service to Managed identity
conect to foundy API in APIM
create subscribtion key
make sure log analytic workspace is created
creage application insight

## Terraform observability modules

The [Application Insights module](IAC/modules/App_insight/main.tf) and
[Grafana module](IAC/modules/Grafana/main.tf) follow the existing module
layout: resources in `main.tf`, typed inputs in the variable file, and
outputs in `output.tf`. The [root configuration](IAC/main.tf) passes the
shared resource group, region, and tags without creating cross-module
resource references.

Application Insights creates a workspace-based `web` component and a
`PerGB2018` Log Analytics workspace with 30-day retention by default.
It routes APIM platform logs and metrics to resource-specific tables.
An API-level diagnostic uses an Application Insights logger with APIM's
system-assigned identity, granted `Monitoring Metrics Publisher` only on
the component. Local ingestion authentication is disabled.

Custom metrics are enabled on the API diagnostic, and Application Insights
is opted into `WithDimensions`. The API diagnostic uses AzAPI because
AzureRM 4.81 does not expose its `metrics` property. JSON bodies use
`jsonencode` for compatibility with this stack's AzAPI 1.x provider.

Request telemetry sampling defaults to 100%, and errors are always logged.
Request/response bodies, headers, and client IP logging are disabled in the
API diagnostic. The existing token-metric policy still emits user/client
dimensions; review those identifiers for privacy and high-cardinality cost
before production use. Metric values alone are not an authoritative billing
or chargeback ledger.

Grafana defaults to Standard with major version 11, public Entra-authenticated
access, and API keys disabled. Its managed identity receives `Monitoring
Reader` on this resource group, not the entire subscription. The Terraform
caller receives `Grafana Admin` by default. For CI deployments, set
`grafana_admin_object_id` to the Entra object ID of the user or group that
should access dashboards, rather than leaving the deployment identity as
the only administrator.

Root inputs you can override:

- `app_insights_name`, `log_analytics_name`, and `grafana_name` default to
  `app-insights-<prefix>`, `log-observability-<prefix>`, and `grafana-<prefix>`.
- `observability_retention_in_days` defaults to `30`.
- `apim_sampling_percentage` defaults to `100`; reduce it for high traffic.
- `grafana_major_version` supports `11` and `12`. Confirm Azure regional
  availability and lifecycle support before deployment.
- `grafana_admin_object_id` accepts an Entra object ID, not an application
  client ID.

The root exports monitoring resource IDs, names, the Grafana endpoint, and
a sensitive Application Insights connection string. Sensitive outputs still
exist in Terraform state; restrict access to the state backend.

Grafana can query the workspace and APIM through its Azure Monitor data
source. No dashboard import or Azure CLI provisioner runs automatically.
After deployment, open the `grafana_endpoint` output and configure/import
an APIM dashboard using the actual subscription, APIM, and workspace.
Role assignments and telemetry can take time to become available.

From `IAC`, validate locally without Azure credentials or remote state:

```powershell
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
terraform test
```

Run the same commands from `IAC\modules\App_insight` and
`IAC\modules\Grafana` for focused tests. Terraform 1.7 or later is required
for mocked providers. CI runs all three directories on pull requests,
matching main-branch pushes, and nightly. Mocked tests verify wiring,
RBAC scopes, sampling, and custom-metric settings; they do not prove live
ingestion, dashboard queries, permissions, or regional availability.

Before a real deployment, authenticate to Azure, initialize without
`-backend=false`, and review `terraform plan`. Confirm this stack has a
dedicated backend state key: the copied provider configuration still uses
`apim.tfstate`, which must not be shared with other independent APIM stacks.
and connect it to log analytics
enablle logger in APIM to connect app insights to APIM

## Testing

run python file to send request to foundry through APIM to get some results and generate logs