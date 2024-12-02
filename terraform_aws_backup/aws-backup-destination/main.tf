terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
  backend "s3" {
    region = "eu-west-2"
    key    = "state"
  }
    required_version = ">= 1.5.0"
}

provider "aws" {
  region  = var.region
  profile = "apim-dev"
  default_tags {
    tags = {
         Environment = local.environment
      }
  }
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

module "destination" {
  source = "./modules/aws_config"

  source_account_name     = "imms-dev" # please note that the assigned value would be the prefix in aws_backup_vault.vault.name
  account_id              = local.destination_account_id
  # source_account_id       = var.source_account_id
  enable_vault_protection = false
}

locals {
  # source_account_id = data.aws_arn.source_terraform_role.account
  environment         = terraform.workspace
  destination_account_id = data.aws_caller_identity.current.account_id
}

variable "region" {
    default = "eu-west-2"
}

# variable "source_terraform_role_arn" {
#   description = "ARN of the terraform role in the source account"
#   type        = string
# }

# data "aws_arn" "source_terraform_role" {
#   arn = var.source_terraform_role_arn
# }