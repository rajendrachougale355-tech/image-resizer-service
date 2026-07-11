# 7. Create a Security Group (Firewall) for the EC2 Instance
resource "aws_security_group" "ec2_sg" {
  name        = "allow_ssh_and_web"
  description = "Allow SSH and HTTP traffic"
  vpc_id      = aws_vpc.devops_project_vpc.id
  # Ensure you have created this key pair in AWS before running Terraform

  # Inbound Rule: Allow SSH (Port 22) so you can log into the server
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # In production, restrict this to your personal IP
  }

  # Inbound Rule: Allow HTTP web traffic (Port 80)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound Rule: Allow the server to talk to the outside world (Crucial for downloading Docker)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # Allows all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "project-ec2-sg"
  }
}

resource "aws_instance" "web_server" {
  # Hardcoded Official Ubuntu 24.04 LTS AMI for ap-south-1 (Mumbai)
  ami                    = "ami-01a00762f46d584a1"
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
   key_name   = "Project_key"

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update -y
              sudo apt-get install -y docker.io
              sudo systemctl start docker
              sudo systemctl enable docker
              sudo usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "devops-project-server"
  }
}