output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.this.id
}

# output "public_subnet_id" {
#   description = "ID of the public subnet"
#   value       = aws_subnet.public.id
# }

output "private_subnet_id" {
  description = "ID of the private subnet (if created)"
  value       = try(aws_subnet.private[0].id, null)
}

output "internet_gateway_id" {
  description = "ID of the internet gateway"
  value       = aws_internet_gateway.this.id
}

output "route_table_id" {
  description = "ID of public route table"
  value       = aws_route_table.public.id
}
