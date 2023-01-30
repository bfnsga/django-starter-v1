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

module "apprunner" {
  source = "./modules/apprunner"

  ## Security Groups
  security_group-apprunner = module.vpc.security_group-apprunner

  ## Subnets
  subnet_private_1 = module.vpc.subnet_private_1
  subnet_private_2 = module.vpc.subnet_private_2
}
