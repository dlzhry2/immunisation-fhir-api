module "get_status" {
    source        = "./lambda"
    prefix        = local.prefix
    short_prefix  = local.short_prefix
    function_name = "get_status"
    source_bucket = aws_s3_bucket.lambda_source_bucket.bucket
    source_key    = aws_s3_object.lambda_function_code.key
    source_sha    = aws_s3_object.lambda_function_code.source_hash
    policy_json   = data.aws_iam_policy_document.logs_policy_document.json
}
