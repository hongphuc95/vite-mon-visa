terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket = "hongphuc-terraform-backend"
    key    = "visa/terraform.tfstate"
    region = "eu-west-3"
  }
}

provider "aws" {
  region = var.region
}