resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.medium"

  tags = {
    Name        = "web-server"
    tenant_id   = "cust_88213"
    environment = "prod"
    service     = "checkout-api"
  }
}

resource "aws_instance" "db" {
  ami           = "ami-87654321"
  instance_type = "r5.large"

  tags = {
    Name        = "db-server"
    tenant_id   = "CUST_88213"
    Environment = "prod"
  }
}
