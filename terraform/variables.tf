variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "name" {
  description = "Name prefix for resources"
  type        = string
  default     = "cyberlence"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Public subnet CIDR block"
  type        = string
  default     = "10.0.1.0/24"
}

variable "public_subnet_cfn_cidr" {
  description = "CIDR block for CloudFormation-created public subnet (use different CIDR to avoid conflicts)"
  type        = string
  default     = "10.0.2.0/24"
}

variable "private_subnet_cidr" {
  description = "Private subnet CIDR block (optional)"
  type        = string
  default     = "10.0.2.0/24"
}

variable "az" {
  description = "Availability zone (optional)"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "create_private" {
  description = "Whether to create a private subnet placeholder"
  type        = bool
  default     = false
}
