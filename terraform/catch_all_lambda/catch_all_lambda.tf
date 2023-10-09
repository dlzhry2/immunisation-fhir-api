resource "aws_s3_bucket" "catch_all_lambda_bucket" {
  bucket        = "${var.prefix}-catch-all-lambda-bucket"
  force_destroy = true
}

data "archive_file" "lambda_function_code_zip" {
  type        = "zip"
  source_file = "../${path.module}/src/catch_all_lambda.py"
  output_path = "build/batch_processing_lambda.zip"
}

#Upload object for the first time, then it gets updated via local-exec
resource "aws_s3_object" "catch_all_lambda_function_code" {
  bucket = aws_s3_bucket.catch_all_lambda_bucket.bucket
  key    = "${var.catch_all_lambda_zip_name}.zip"
  source = "./zips/catch_all_lambda_function_code.zip"  # Local path to your ZIP file
}

resource "aws_lambda_function" "catch_all_lambda" {
  depends_on  = [null_resource.catch_all_lambda_dist,
                aws_s3_object.catch_all_lambda_function_code
  ]
  s3_bucket=aws_s3_bucket.catch_all_lambda_bucket.bucket
  s3_key  ="${var.catch_all_lambda_zip_name}.zip"
  function_name = "${var.prefix}-catch-all-lambda"
#   source_code_hash = data.aws_s3_object.catch_all_lambda_function_code.etag  # Calculate the hash of the new ZIP file uploaded to s3
  role          = aws_iam_role.catch_all_lambda_role.arn
  handler       = "catch_all_lambda.handler"
  runtime       = "nodejs18.x"
  memory_size   = 1024

  environment {
    variables = {}
  }
}

output "catch_all_lambda_function_name" {
  value = aws_lambda_function.catch_all_lambda.function_name
}

output "catch_all_lambda_zip_name" {
  value = aws_lambda_function.catch_all_lambda.s3_key
}

