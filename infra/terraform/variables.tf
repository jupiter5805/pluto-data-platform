variable "aws_region" {
  type        = string
  description = "AWS region."
  default     = "eu-west-2"
}

variable "project_name" {
  type        = string
  description = "Resource name prefix."
  default     = "pluto-data-platform"
}

variable "db_username" {
  type        = string
  description = "RDS master username."
  default     = "pluto_admin"
}
