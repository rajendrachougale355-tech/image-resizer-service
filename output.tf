
# 10. Output the Public IP address of the server when deployment completes
output "server_public_ip" {
  value       = aws_instance.web_server.public_ip
  description = "The public IP address of your main server."
}