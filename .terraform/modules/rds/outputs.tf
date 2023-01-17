############################################
## DATABASE HOST
############################################
output "database_host" {
  value = aws_db_instance.default.address
}