variable "region" {
  description = "aws region"
  default     = "us-east-2"
}

variable "account_id" {
  description = "AWS Account ID"
  default = "386283720018"
}

variable "prefix" {
  description = "objects prefix"
  default     = "tbat"
}

# Prefix configuration and project common tags
locals {
  glue_bucket = "${var.prefix}-${var.bucket_names[3]}-${var.account_id}"
  prefix      = var.prefix
  common_tags = {
    Project = "tcc-tbat-cesar"
  }
}

variable "bucket_names" {
  description = "s3 bucket names"
  type        = list(string)
  default = [
    "raw",
    "processed",
    "result-athena",
    "aws-glue-scripts"
  ]
}

variable "glue_job_role_arn" {
  description = "The ARN of the IAM role associated with this job."
  default     = null
}