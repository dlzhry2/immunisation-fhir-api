# Define the directory containing the Docker image and calculate its SHA-256 hash for triggering redeployments
locals {
  filenameconverter_lambda_dir = abspath("${path.root}/../../meshtest")
  filenameconverter_lambda_files         = fileset(local.filenameconverter_lambda_dir, "**")
  filenameconverter_lambda_dir_sha       = sha1(join("", [for f in local.filenameconverter_lambda_files  : filesha1("${local.filenameconverter_lambda_dir}/${f}")]))
}


resource "aws_ecr_repository" "mesh_file_converter_lambda_repository" {
  image_scanning_configuration {
    scan_on_push = true
  }
  name = "immunisation-meshconverter-repo"
}

# Module for building and pushing Docker image to ECR
module "mesh_converter_docker_image" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = false
  ecr_repo        = aws_ecr_repository.mesh_file_converter_lambda_repository.name
  ecr_repo_lifecycle_policy = jsonencode({
    "rules" : [
      {
        "rulePriority" : 1,
        "description" : "Keep only the last 2 images",
        "selection" : {
          "tagStatus" : "any",
          "countType" : "imageCountMoreThan",
          "countNumber" : 2
        },
        "action" : {
          "type" : "expire"
        }
      }
    ]
  })

  platform      = "linux/amd64"
  use_image_tag = false
  source_path   = local.filenameconverter_lambda_dir
  triggers = {
    dir_sha = local.filenameconverter_lambda_dir_sha
  }
}

# Define the lambdaECRImageRetreival policy
resource "aws_ecr_repository_policy" "meshfileconverter_lambda_ECRImageRetreival_policy" {
  repository = aws_ecr_repository.mesh_file_converter_lambda_repository.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Sid": "LambdaECRImageRetrievalPolicy",
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": [
          "ecr:BatchGetImage",
          "ecr:DeleteRepositoryPolicy",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetRepositoryPolicy",
          "ecr:SetRepositoryPolicy"
        ],
        "Condition": {
          "StringLike": {
            "aws:sourceArn": "arn:aws:lambda:eu-west-2:${local.local_account_id}:function:immunisation-meshfileconverter_lambda"
          }
        }
      }
  ]
  })
}

# IAM Role for Lambda
resource "aws_iam_role" "meshfileconverter_lambda_exec_role" {
  name = "immunisation-meshfileconverter-lambda-exec-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Sid = "",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

# Policy for Lambda execution role
resource "aws_iam_policy" "meshfileconverter_lambda_exec_policy" {
  name   = "immunisation-meshfileconverter-lambda-exec-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
       Resource = "arn:aws:logs:${var.aws_region}:${local.local_account_id}:log-group:/aws/lambda/immunisation-meshfileconverter_lambda:*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject",
          "s3:CopyObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::immunisation-batch-internal-dev-data-sources",           
          "arn:aws:s3:::immunisation-batch-internal-dev-data-sources/*"        
        ]
      },
      {
        Effect   = "Allow"
        Action   = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject",
          "s3:CopyObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::local-immunisation-mesh",           
          "arn:aws:s3:::local-immunisation-mesh/*"        
        ]
      }     
      # {
      #   "Effect": "Allow",
      #   "Action": [
      #     "firehose:PutRecord",
      #     "firehose:PutRecordBatch"
      #   ],
      #   "Resource": "arn:aws:firehose:*:*:deliverystream/${module.splunk.firehose_stream_name}"
      # },      
    ]
  })
}

# Attach the execution policy to the Lambda role
resource "aws_iam_role_policy_attachment" "meshfileconverter_lambda_exec_policy_attachment" {
  role       = aws_iam_role.meshfileconverter_lambda_exec_role.name
  policy_arn = aws_iam_policy.meshfileconverter_lambda_exec_policy.arn
}



# Lambda Function with Security Group and VPC.
resource "aws_lambda_function" "mesh_file_converter_lambda" {
  function_name   = "immunisation-meshfileconverter_lambda"
  role            = aws_iam_role.meshfileconverter_lambda_exec_role.arn
  package_type    = "Image"
  image_uri       = module.mesh_converter_docker_image.image_uri
  architectures   = ["x86_64"]
  timeout         = 360
 
}

# environment {
#     variables = {
#       SOURCE_BUCKET_NAME   = "${local.batch_prefix}-data-sources"
#       ACK_BUCKET_NAME      = data.aws_s3_bucket.existing_destination_bucket.bucket
#       QUEUE_URL           = aws_sqs_queue.supplier_fifo_queue.url
#       CONFIG_BUCKET_NAME   = data.aws_s3_bucket.existing_config_bucket.bucket
#       REDIS_HOST           = data.aws_elasticache_cluster.existing_redis.cache_nodes[0].address
#       REDIS_PORT           = data.aws_elasticache_cluster.existing_redis.cache_nodes[0].port
#       SPLUNK_FIREHOSE_NAME = module.splunk.firehose_stream_name
#       AUDIT_TABLE_NAME     = "${data.aws_dynamodb_table.audit-table.name}"
#       FILE_NAME_GSI        = "filename_index"
#       FILE_NAME_PROC_LAMBDA_NAME = "imms-${local.env}-filenameproc_lambda"

#     }
#   }


# Permission for S3 to invoke Lambda function
resource "aws_lambda_permission" "s3_invoke_permission" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mesh_file_converter_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::local-immunisation-mesh"
}

# S3 Bucket notification to trigger Lambda function
resource "aws_s3_bucket_notification" "datasources_lambda_notification" {
  bucket = "local-immunisation-mesh"

  lambda_function {
    lambda_function_arn = aws_lambda_function.mesh_file_converter_lambda.arn
    events              = ["s3:ObjectCreated:*"]
    #filter_prefix      =""
  }
}

resource "aws_cloudwatch_log_group" "file_name_processor_log_group" {
  name              = "/aws/lambda/immunisation-meshfileconverter_lambda"
  retention_in_days = 30
}