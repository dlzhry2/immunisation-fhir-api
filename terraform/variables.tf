variable "project_name" {

}

variable "project_short_name" {

}

variable "service" {
  default = "fhir-api"
}

locals {
  environment         = terraform.workspace
  prefix              = "${var.project_name}-${var.service}-${local.environment}"
  short_prefix        = "${var.project_short_name}-${local.environment}"

  tags = {
    Project     = var.project_name
    Environment = local.environment
    Service     = var.service
  }
}

variable "region" {
  default = "eu-west-2"
}