#########################
## AppRunner
#########################

#########################
## VPC CONNECTOR
#########################
resource "aws_apprunner_vpc_connector" "connector" {
  vpc_connector_name = "vpc-connector"
  subnets            = [var.subnet_private_1, var.subnet_private_2]
  security_groups    = [var.security_group-apprunner]
}

## IAM - Access Role
#########################
resource "aws_iam_role" "apprunner-access_role" {
  name = "AppRunnerAccessRole"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "build.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "apprunner-access_policy" {
  name        = "AppRunnerAccessPolicy"
  description = "Allows AppRunner access to ECR Private Repository."

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Resource" : "*",
        "Action" : [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchGetImage",
          "ecr:DescribeImages",
          "ecr:GetAuthorizationToken"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "apprunner-access_role_policy" {
  role       = aws_iam_role.apprunner-access_role.name
  policy_arn = aws_iam_policy.apprunner-access_policy.arn
}

## IAM - Instance Role
#########################
resource "aws_iam_role" "apprunner-instance_role" {
  name = "AppRunnerInstanceRole"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "tasks.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "apprunner-instance_policy" {
  name        = "AppRunnerInstancePolicy"
  description = "Allows AppRunner access AWS resources."

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Resource" : "*",
        "Action" : [
          "s3:PutObject",
          "s3:GetObject"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "apprunner-instance_role_policy" {
  role       = aws_iam_role.apprunner-instance_role.name
  policy_arn = aws_iam_policy.apprunner-instance_policy.arn
}

## AppRunner Service
#########################
resource "aws_apprunner_service" "apprunner" {
  service_name = "django-starter-v1"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner-access_role.arn
    }

    image_repository {
      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          "SECRET_KEY" = var.secret_key
          "DATABASE_HOST" = var.database_host
          "DATABASE_PASSWORD" = var.database_password
          "AUTH0_CLIENT_ID" = var.auth0_client_id
          "AUTH0_CLIENT_SECRET" = var.auth0_client_secret
          "AUTH0_DOMAIN" = var.auth0_domain
          "STRIPE_API_KEY" = var.stripe_api_key
          "SERVICE_DOMAIN" = "$APPS_DOMAIN"
        }
      }
      image_identifier      = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/django-starter-v1:latest"
      image_repository_type = "ECR"
    }

    auto_deployments_enabled = false
  }

  network_configuration {
    egress_configuration {
        egress_type = "VPC"
        vpc_connector_arn = aws_apprunner_vpc_connector.connector.arn
    }
  }

  instance_configuration {
    instance_role_arn = aws_iam_role.apprunner-instance_role.arn
  }

  depends_on = [
    aws_iam_role_policy_attachment.apprunner-access_role_policy,
    aws_iam_role_policy_attachment.apprunner-instance_role_policy,
    aws_apprunner_vpc_connector.connector
  ]
}

#########################
## CLOUDWATCH LOG GROUP
#########################
resource "aws_cloudwatch_log_group" "apprunner-application" {
  name              = "/aws/apprunner/${aws_apprunner_service.apprunner.service_name}/${aws_apprunner_service.apprunner.service_id}/application"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "apprunner-service" {
  name              = "/aws/apprunner/${aws_apprunner_service.apprunner.service_name}/${aws_apprunner_service.apprunner.service_id}/service"
  retention_in_days = 14
}