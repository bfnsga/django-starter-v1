####################
## Service variables
####################
variable "security_group-apprunner" {
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

####################
## Environment variables
####################
variable "secret_key" {
    type = "string"
}

variable "database_host" {
    type = "string"
}

variable "database_password" {
    type = "string"
}

variable "auth0_client_id" {
    type = "string"
}

variable "auth0_client_secret" {
    type = "string"
}

variable "auth0_domain" {
    type = "string"
}

variable "stripe_api_key" {
    type = "string"
}
