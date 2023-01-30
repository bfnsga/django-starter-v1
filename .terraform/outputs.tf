############################################
## SECURITY GROUPS
############################################
output "security_group-apprunner" {
  value = module.vpc.security_group-apprunner
}

############################################
## SUBNETS
############################################
output "subnet_private_1" {
  value = module.vpc.subnet_private_1
}

output "subnet_private_2" {
  value = module.vpc.subnet_private_2
}