############################################
## SECURITY GROUPS
############################################
output "security_group-apprunner" {
  value = aws_security_group.apprunner.id
}

output "security_group-database" {
  value = aws_security_group.database.id
}

############################################
## SUBNETS
############################################
output "subnet_private_1" {
  value = aws_subnet.private_1.id
}

output "subnet_private_2" {
  value = aws_subnet.private_2.id
}