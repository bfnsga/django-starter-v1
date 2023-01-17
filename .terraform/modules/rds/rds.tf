############################################
## SUBNET GROUP
############################################
resource "aws_db_subnet_group" "default" {
  name       = "django-starter-v1"
  subnet_ids = [var.subnet_private_1, var.subnet_private_2]
}

############################################
## AURORA V2 CLUSTER
############################################
resource "aws_db_instance" "default" {
  identifier           = "django-starter-v1"
  db_subnet_group_name = aws_db_subnet_group.default.name
  allocated_storage    = 20
  max_allocated_storage = 1000
  db_name              = "defaultdb"
  engine               = "postgres"
  engine_version       = "14.5"
  instance_class       = "db.t3.micro"
  username             = "djangoadmin"
  password             = var.database_password
  skip_final_snapshot  = true
  storage_type         = "gp2"
  vpc_security_group_ids = [var.security_group-database]
  storage_encrypted    = true
  apply_immediately    = true
  network_type = "IPV4"
  auto_minor_version_upgrade = true
  allow_major_version_upgrade = false
}

# Add maintenance window