variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "region" {
  type        = string
  description = "AWS Region"
  default     = "eu-west-3"
}

variable "spot_price" {
  type        = string
  description = "Max price to pay for spot instances"
}

variable "instance_type" {
  type        = string
  description = "Instance type"
}

variable "ssh_key" {
  type        = string
  description = "SSH key name"
}
