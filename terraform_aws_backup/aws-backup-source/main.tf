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
      Project     = var.project_name
      Environment = local.environment
      }
  }
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

variable "region" {
    default = "eu-west-2"
}

locals{
  destination_vault_arn="arn:aws:backup:eu-west-2:345594581768:backup-vault:imms-dev-backup-vault"
}

module "source" {
  source = "./modules/aws_config"

  backup_copy_vault_account_id = local.destination_account_id
  backup_copy_vault_arn        = local.destination_vault_arn
  environment_name      = terraform.workspace
  project_name          = "imms-fhir-api"
  terraform_role_arn    = local.terraform_role_arn
  
  backup_plan_config = {
    "compliance_resource_types" : [
      "S3"
    ],
    "rules" : [
      {
        "copy_action" : {
          "delete_after" : 4
        },
        "lifecycle" : {
          "delete_after" : 2
        },
        "name" : "daily_kept_for_2_days",
        "schedule" : "cron(0 0 * * ? *)"
      }
    ],
    "selection_tag" : "NHSE-Enable-Backup"
  }

  backup_plan_config_dynamodb = {
    "compliance_resource_types" : [
      "DynamoDB"
    ],
    "enable" : true,
    "rules" : [
      {
        "copy_action" : {
          "delete_after" : 4
        },
        "lifecycle" : {
          "delete_after" : 2
        },
        "name" : "daily_kept_for_2_days",
        "schedule" : "cron(0 0 * * ? *)"
      }
    ],
    "selection_tag" : "NHSE-Enable-Backup"
  }
}