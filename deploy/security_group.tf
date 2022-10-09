data "aws_vpc" "main" {
  id = var.vpc_id
}

locals {
  ingess_rule = [
    {
      port        = 80
      description = "Allow HTTP traffics"
    },
    {
      port        = 22
      description = "Allow SSH traffics"
    },
  ]
}

resource "aws_security_group" "visa" {
  name   = "visa"
  vpc_id = data.aws_vpc.main.id

  dynamic "ingress" {
    for_each = local.ingess_rule

    content {
      description = ingress.value.description
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    terraform = "true"
    env       = "dev"
  }
}