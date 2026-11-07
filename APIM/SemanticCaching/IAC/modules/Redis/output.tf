output "redis_id" {
  value = azurerm_managed_redis.redis.id
}

output "redis_name" {
  value = azurerm_managed_redis.redis.name
}

output "redis_hostname" {
  value = azurerm_managed_redis.redis.hostname
}

output "redis_port" {
  value = azurerm_managed_redis.redis.default_database[0].port
}

output "redis_connection_string" {
  value     = "${azurerm_managed_redis.redis.hostname}:${azurerm_managed_redis.redis.default_database[0].port},password=${azurerm_managed_redis.redis.default_database[0].primary_access_key},ssl=True,abortConnect=False"
  sensitive = true
}