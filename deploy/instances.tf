data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_spot_instance_request" "visa-worker" {
  ami           = data.aws_ami.ubuntu.id
  spot_price    = var.spot_price
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.visa.id]
  key_name                               = var.ssh_key
  user_data                              = file("userdata.yaml")

  tags = {
    terraform = "true"
    env       = "dev"
  }
}