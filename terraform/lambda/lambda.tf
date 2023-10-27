resource "aws_lambda_function" "lambda" {
    role          = aws_iam_role.lambda_role.arn
    timeout       = 300
    s3_bucket     = var.source_bucket
    s3_key        = var.source_key
    function_name = "${var.short_prefix}_${var.function_name}"
    handler       = "${var.function_name}_handler.${var.function_name}_handler"
    runtime       = "python3.9"

    source_code_hash = var.source_sha

    environment {
        variables = var.environments
    }
}


