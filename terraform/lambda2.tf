locals {
    lambda_source_dir    = "${path.root}/../lambda_code"
    lambda_source_zip    = "build/lambda_source_code.zip"
    endpoint_policy_path = "${path.root}/policies/lambda_endpoint.json"
}

data "archive_file" "lambda_source_zip" {
    type        = "zip"
    source_dir  = local.lambda_source_dir
    output_path = local.lambda_source_zip
}

resource "aws_s3_bucket" "lambda_source_code" {
    bucket        = "${local.prefix}-lambda-source-code"
    force_destroy = true
}

resource "aws_s3_object" "lambda_function_code" {
    bucket = aws_s3_bucket.lambda_source_code.bucket
    key    = "lambda_code"
    source = data.archive_file.lambda_source_zip.output_path
    etag   = filemd5(data.archive_file.lambda_source_zip.output_path)
}
data "aws_iam_policy_document" "endpoint_policy_document" {
    source_policy_documents = [templatefile(local.endpoint_policy_path, {} )]
}

module "get_status" {
    source        = "./lambda2"
    prefix        = local.prefix
    short_prefix  = local.short_prefix
    function_name = "get_status"
    source_bucket = aws_s3_bucket.lambda_source_code.bucket
    source_key    = "lambda_code"
    policy_json   = data.aws_iam_policy_document.endpoint_policy_document.json
}

module "get_event" {
    source        = "./lambda2"
    prefix        = local.prefix
    short_prefix  = local.short_prefix
    function_name = "get_event"
    source_bucket = aws_s3_bucket.lambda_source_code.bucket
    source_key    = "lambda_code"
    policy_json   = data.aws_iam_policy_document.endpoint_policy_document.json
}
