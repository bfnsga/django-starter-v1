############################################
## IAM
############################################
output "github_actions_role-arn" {
    value = module.iam.github_actions_role-arn
}

############################################
## VPC
############################################
output "security_group-apprunner" {
  value = module.vpc.security_group-apprunner
}

output "subnet_private_1" {
  value = module.vpc.subnet_private_1
}

output "subnet_private_2" {
  value = module.vpc.subnet_private_2
}

############################################
## DATABASE
############################################
output "database_host" {
    value = module.rds.database_host
}