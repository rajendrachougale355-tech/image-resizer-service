resource "aws_vpc" "devops_project_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "devops_project_vpc"
  }

}


resource "aws_internet_gateway" "project-igw" {
  vpc_id = aws_vpc.devops_project_vpc.id

  tags = {
    Name = "project-igw"
  }
}
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.devops_project_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "ap-south-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "devops_project_subnet"
  }
}
resource "aws_subnet" "private_subnet" {
  vpc_id            = aws_vpc.devops_project_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "ap-south-1b"

  tags = {
    Name = "devops_project_private_subnet"
  }
}
resource "aws_route_table" "public-rt" {
  vpc_id = aws_vpc.devops_project_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.project-igw.id
  }
  tags = {
    Name = "project-public-rt"
  }
}
resource "aws_route_table_association" "public-rt-association" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public-rt.id
}