provider "aws" {
  alias  = "source"
  region = "eu-west-2"
}

variable "destination_vault_arn" {
  description = "ARN of the backup vault in the destination account"
  type        = string
  default     = ""
}

#data "aws_arn" "destination_vault_arn" {
#  arn = var.destination_vault_arn
#}

#data "aws_secretsmanager_secret" "backup-account-secret" {
#  name = "nhsd-nrlf--dev--test-backup-account-id"
#}
data "aws_secretsmanager_secret_version" "destination_account_id" {
  secret_id = data.aws_secretsmanager_secret.backup-account-secret.id
}

locals {
  # Adjust these as required
  project_name     = "dev-backups-poc"
  environment_name = "dev"

  source_account_id = data.aws_caller_identity.current.account_id
  destination_account_id = data.aws_caller_identity.current.account_id
  #destination_account_id = data.aws_secretsmanager_secret_version.destination_account_id.secret_string
}

# First, we create an S3 bucket for compliance reports.
resource "aws_s3_bucket" "backup_reports" {
  bucket_prefix = "${local.project_name}-backup-reports"
}

resource "aws_s3_bucket_public_access_block" "backup_reports" {
  bucket = aws_s3_bucket.backup_reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backup_reports" {
  bucket = aws_s3_bucket.backup_reports.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_policy" "backup_reports_bucket_policy" {
  bucket = aws_s3_bucket.backup_reports.id

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "backup_reports_bucket_policy"
    Statement = [
      {
        Sid       = "HTTPSOnly"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.backup_reports.arn,
          "${aws_s3_bucket.backup_reports.arn}/*",
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
    ]
  })
}


resource "aws_s3_bucket_ownership_controls" "backup_reports" {
  bucket = aws_s3_bucket.backup_reports.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "backup_reports" {
  depends_on = [aws_s3_bucket_ownership_controls.backup_reports]

  bucket = aws_s3_bucket.backup_reports.id
  acl    = "private"
}

# We need a key for the SNS topic that will be used for notifications from AWS Backup. This key
# will be used to encrypt the messages sent to the topic before they are sent to the subscribers,
# but isn't needed by the recipients of the messages.

# First we need some contextual data
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Now we can define the key itself
resource "aws_kms_key" "backup_notifications" {
  description             = "KMS key for AWS Backup notifications"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Sid    = "Enable IAM User Permissions"
        Principal = {
          AWS = "arn:aws:iam::${local.source_account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Effect = "Allow"
        Principal = {
          Service = "sns.amazonaws.com"
        }
        Action   = ["kms:GenerateDataKey*", "kms:Decrypt"]
        Resource = "*"
      },
    ]
  })
}

# Now we can deploy the source and destination modules, referencing the resources we've created above.

module "source" {
  source = "/aws-backup-source"

  backup_copy_vault_account_id = local.destination_account_id
  #  backup_copy_vault_arn              = data.aws_arn.destination_vault_arn.arn
  environment_name      = local.environment_name
  bootstrap_kms_key_arn = aws_kms_key.backup_notifications.arn
  project_name          = local.project_name
  reports_bucket        = aws_s3_bucket.backup_reports.bucket
  #terraform_role_arn                = data.aws_caller_identity.current.arn
  terraform_role_arn = "arn:aws:iam::${var.assume_account}:role/${var.assume_role}"

  notification_target_email_addresses = local.notification_emails

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