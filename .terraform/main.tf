module "iam" {
  source = "./modules/iam"
}

module "vpc" {
  source = "./modules/vpc"
}

module "rds" {
  source = "./modules/rds"

  ## Security Groups
  security_group-database = module.vpc.security_group-database

  ## Database Credentials
  database_password = var.database_password

  ## Subnets
  subnet_private_1 = module.vpc.subnet_private_1
  subnet_private_2 = module.vpc.subnet_private_2

  ## AWS Metadata
  aws_account_id = var.aws_account_id
  aws_region = var.aws_region

  depends_on = [
    module.vpc
  ]
}

module "ecr" {
  source = "./modules/ecr"
}

#module "apprunner" {
#  source = "./modules/apprunner"

  ## Security Groups
#  security_group-apprunner = module.vpc.security_group-apprunner

  ## Subnets
#  subnet_private_1 = module.vpc.subnet_private_1
#  subnet_private_2 = module.vpc.subnet_private_2

  ## AWS Metadata
#  aws_account_id = var.aws_account_id
#  aws_region = var.aws_region

  ## AppRunner Environment Variables
#  database_host = module.rds.database_host
#  database_password = var.database_password

#  secret_key = var.secret_key
#  auth0_client_id = var.auth0_client_id
#  auth0_client_secret = var.auth0_client_secret
#  auth0_domain = var.auth0_domain
#  stripe_api_key = var.stripe_api_key
#}
