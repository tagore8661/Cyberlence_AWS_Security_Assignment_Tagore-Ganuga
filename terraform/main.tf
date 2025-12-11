resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = merge(var.tags, { Name = var.name })
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  tags   = merge(var.tags, { Name = "${var.name}-igw" })
}

# resource "aws_subnet" "public" {
#   vpc_id                  = aws_vpc.this.id
#   cidr_block              = var.public_subnet_cidr
#   availability_zone       = var.az
#   map_public_ip_on_launch = true
#   tags                    = merge(var.tags, { Name = "${var.name}-public-subnet" })
# }

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id
  tags   = merge(var.tags, { Name = "${var.name}-public-rt" })
}

resource "aws_route" "public_default" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this.id
}

# resource "aws_route_table_association" "public_assoc" {
#   subnet_id      = aws_subnet.public.id
#   route_table_id = aws_route_table.public.id
# }

/* Optional: private subnet + NAT Gateway (disabled by default) */
resource "aws_subnet" "private" {
  count         = var.create_private ? 1 : 0
  vpc_id        = aws_vpc.this.id
  cidr_block    = var.private_subnet_cidr
  availability_zone = var.az
  map_public_ip_on_launch = false
  tags = merge(var.tags, { Name = "${var.name}-private-subnet" })
}

