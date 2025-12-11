resource "aws_cloudformation_stack" "public_subnet_stack" {
  name = "${var.name}-public-subnet-cfn"

  template_body = file("${path.module}/templates/public-subnet-cfn.yaml")

  parameters = {
    VpcId            = aws_vpc.this.id
    InternetGatewayId = aws_internet_gateway.this.id
    PublicCidr       = var.public_subnet_cfn_cidr
    RouteTableId     = aws_route_table.public.id
    #SubnetId         = aws_subnet.public.id
  }

  capabilities = ["CAPABILITY_NAMED_IAM"]
}

output "cfn_public_subnet_id" {
  value = try(aws_cloudformation_stack.public_subnet_stack.outputs["PublicSubnetId"], null)
}
