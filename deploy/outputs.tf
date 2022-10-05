output "visa_public_ip" {
  description = "Public IP address of the instance hosted visa image"
  value       = aws_spot_instance_request.visa-worker.public_ip
}