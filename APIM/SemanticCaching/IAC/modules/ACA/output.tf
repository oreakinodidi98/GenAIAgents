output "aca_id" {
  value = azurerm_container_app.aca-redis-stack.id
}

output "aca_name" {
  value = azurerm_container_app.aca-redis-stack.name
}

output "aca_environment_id" {
  value = azurerm_container_app_environment.aca-env.id
}

output "aca_hostname" {
  value = azurerm_container_app.aca-redis-stack.ingress[0].fqdn
}

output "aca_connection_string" {
  value     = "${azurerm_container_app.aca-redis-stack.ingress[0].fqdn}:6379,password=${random_password.redis.result},ssl=False,abortConnect=False"
  sensitive = true
}

output "apim_subnet_id" {
  value = azurerm_subnet.snet-apim.id

  depends_on = [
    azurerm_private_dns_zone_virtual_network_link.aca,
    azurerm_private_dns_a_record.aca,
  ]
}

output "aca_vnet_id" {
  value = azurerm_virtual_network.vnet-aca.id
}