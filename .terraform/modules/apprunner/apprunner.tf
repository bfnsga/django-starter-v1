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
          "s3:GetObject",
          "secretsmanager:GetSecretValue",
          "kms:Decrypt*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "apprunner-instance_role_policy" {
  role       = aws_iam_role.apprunner-instance_role.name
  policy_arn = aws_iam_policy.apprunner-instance_policy.arn
}