resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  resource_group_name = var.resourcegroup
  location            = var.location
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "snet_aca" {
  name                            = var.subnet_name
  resource_group_name             = var.resourcegroup
  virtual_network_name            = var.vnet_name
  address_prefixes                = ["10.0.1.0/26"]
  default_outbound_access_enabled = true

  delegation {
    name = "delegation"

    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}