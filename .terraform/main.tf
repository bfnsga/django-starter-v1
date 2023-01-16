module "vpc" {
  source = "./modules/vpc"
}

module "rds" {
  source = "./modules/rds"

  ## Security Groups
  security_group-database = module.vpc.security_group-database

  ## Database Credentials
  db_username = var.db_username
  db_password = var.db_password

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