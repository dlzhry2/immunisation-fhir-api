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
      Service     = var.service
    }
  }
}

provider "aws" {
  alias   = "acm_provider"
  region  = var.region
  profile = "apim-dev"
}
