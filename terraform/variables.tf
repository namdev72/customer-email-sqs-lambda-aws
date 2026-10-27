variable "aws_region" {
  type        = string
  description = "AWS Region"
}

variable "project_name" {
  description = "project name"
  type        = string
}

variable "sender_email" {
  description = "Verified SES sender email address"
  type        = string
}