# Define the directory containing the Docker image and calculate its SHA-256 hash for triggering redeployments
locals {
  lambda_dir = abspath("${path.root}/../ackessor")
  lambda_files         = fileset(local.lambda_dir, "**")
  lambda_dir_sha       = sha1(join("", [for f in local.lambda_files : filesha1("${local.lambda_dir}/${f}")]))
}


resource "aws_ecr_repository" "ack_lambda_repository" {
  image_scanning_configuration {
    scan_on_push = true
  }
  name = "imms-ack-repo"
}

# Module for building and pushing Docker image to ECR
module "file_processor_docker_image" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = false
  ecr_repo        = aws_ecr_repository.ack_lambda_repository.name
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
  source_path   = local.lambda_dir
  triggers = {
    dir_sha = local.lambda_dir_sha
  }
}

# Define the lambdaECRImageRetreival policy
resource "aws_ecr_repository_policy" "ack_lambda_ECRImageRetreival_policy" {
  repository = aws_ecr_repository.ack_lambda_repository.name

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
            "aws:sourceArn": "arn:aws:lambda:eu-west-2:345594581768:function:imms-ack-lambda"
          }
        }
      }
  ]
  })
}

# IAM Role for Lambda
resource "aws_iam_role" "ack_lambda_exec_role" {
  name = "imms-ack-lambda-exec-role"
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
resource "aws_iam_policy" "ack_lambda_exec_policy" {
  name   = "imms-ack-lambda-exec-policy"
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
       Resource = "arn:aws:logs:eu-west-2:345594581768:log-group:/aws/lambda/imms-ack-lambda:*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::immunisation-batch-pr-96-data-destinations",           
          "arn:aws:s3:::immunisation-batch-pr-96-data-destinations/*"        
        ]
      }
    ]
  })
}

# Policy for Lambda to interact with SQS
resource "aws_iam_policy" "ack_lambda_sqs_policy" {
  name = "imms-ack-lambda-sqs-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "sqs:SendMessage"
      ],
      Resource = [
        aws_sqs_queue.fifo_queue.arn
      ]
    }]
  })
}

resource "aws_iam_policy" "ack_s3_kms_access_policy" {
  name        = "imms-ack-s3-kms-policy"
  description = "Allow Lambda to decrypt environment variables"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:GenerateDataKey*"
        ]
        Resource = "arn:aws:kms:eu-west-2:345594581768:key/9bbfbfd9-1745-4325-a9b7-33d1f6be89c1"
      }
    ]
  })
}

# Attach the execution policy to the Lambda role
resource "aws_iam_role_policy_attachment" "lambda_exec_policy_attachment" {
  role       = aws_iam_role.ack_lambda_exec_role.name
  policy_arn = aws_iam_policy.ack_lambda_exec_policy.arn
}

# Attach the SQS policy to the Lambda role
resource "aws_iam_role_policy_attachment" "lambda_sqs_policy_attachment" {
  role       = aws_iam_role.ack_lambda_exec_role.name
  policy_arn = aws_iam_policy.ack_lambda_sqs_policy.arn
}

# Attach the kms policy to the Lambda role
resource "aws_iam_role_policy_attachment" "lambda_kms_policy_attachment" {
  role       = aws_iam_role.ack_lambda_exec_role.name
  policy_arn = aws_iam_policy.ack_s3_kms_access_policy.arn
}
# Lambda Function with Security Group and VPC.
resource "aws_lambda_function" "file_processor_lambda" {
  function_name   = "imms-ack-lambda"
  role            = aws_iam_role.ack_lambda_exec_role.arn
  package_type    = "Image"
  image_uri       = module.file_processor_docker_image.image_uri
  architectures   = ["x86_64"]
  timeout         = 60

  vpc_config {
    subnet_ids         = data.aws_subnets.default.ids
    security_group_ids = [data.aws_security_group.existing_sg.id]
  }

  reserved_concurrent_executions = 20
}