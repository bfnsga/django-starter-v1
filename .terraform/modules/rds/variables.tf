####################
## FROM MAIN.TF
####################
variable "security_group-database" {
  type = string
}

variable "subnet_private_1" {
  type = string
}

variable "subnet_private_2" {
  type = string
}

variable "aws_account_id" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "db_username" {
  type = string
}

variable "db_password" {
  type = string
}