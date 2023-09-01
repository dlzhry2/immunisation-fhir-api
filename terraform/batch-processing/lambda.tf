locals {
  lambda_file_name = "batch_processing.py"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/${local.lambda_file_name}"
  output_path = "build/batch_processing_lambda.zip"
}

resource "aws_lambda_function" "batch_processing_lambda" {
    function_name    = "${var.short_prefix}-token-validator-lambda"
    role             = aws_iam_role.lambda_role.arn
    timeout          = 300
    filename         = data.archive_file.lambda_zip.output_path
    source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}

resource "aws_s3_bucket_notification" "s3-source-lambda-trigger" {
    bucket = "${aws_s3_bucket.source.id}"
    lambda_function {
        lambda_function_arn = "${aws_lambda_function.batch_processing_lambda.arn}"
        events = ["s3:ObjectCreated:*"]
    }
}

resource "aws_lambda_permission" "s3-permission-to-trigger-lambda" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.batch_processing_lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.source.arn
}
