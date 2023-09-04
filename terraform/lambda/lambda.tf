resource "aws_lambda_function" "imms_lambda" {
  depends_on  = [aws_s3_bucket.lambda_bucket,
              null_resource.lambda_typescript_dist
  ]
  s3_bucket = aws_s3_bucket.lambda_bucket.bucket
  s3_key    = "${var.api_version}/${var.lambda_zip_name}.zip"
  function_name = "${var.prefix}-lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "nodejs18.x"
  memory_size   = 1024
  timeout       = 300
}

output "imms_lambda_function_name" {
  value = aws_lambda_function.imms_lambda.function_name
}

