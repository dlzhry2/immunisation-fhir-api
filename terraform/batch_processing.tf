locals {
    // Flag so we can force delete s3 buckets with items in for pr and shortcode environments only.
    is_temp = length(regexall("[a-z]{2,4}-?[0-9]+", local.environment)) > 0
}

resource "aws_s3_bucket" "batch_data_source_bucket" {
    bucket        = "${local.prefix}-batch-data-source"
    force_destroy = local.is_temp
}

resource "aws_s3_bucket" "batch_data_destination_bucket" {
    bucket        = "${local.prefix}-batch-data-destination"
    force_destroy = local.is_temp
}

data "aws_iam_policy_document" "batch_processing_policy_document" {
    source_policy_documents = [
        templatefile("${local.policy_path}/batch_processing.json", {
            "batch_processing_source_bucket" : aws_s3_bucket.batch_data_source_bucket.bucket
            "batch_processing_destination_bucket" : aws_s3_bucket.batch_data_destination_bucket.bucket
        } ),
        templatefile("${local.policy_path}/log.json", {} ),
    ]
}

locals {
    batch_processing_lambda_name = "batch_processing"
}
module "batch_processing" {
    source        = "./lambda"
    prefix        = local.prefix
    short_prefix  = local.short_prefix
    function_name = local.batch_processing_lambda_name
#    source_bucket = aws_s3_bucket.lambda_source_bucket.bucket
#    source_key    = aws_s3_object.lambda_function_code.key
#    source_sha    = aws_s3_object.lambda_function_code.source_hash
    image_uri     = module.docker_image.image_uri
    policy_json   = data.aws_iam_policy_document.batch_processing_policy_document.json
    environments  = {
        "SERVICE_DOMAIN_NAME" = module.api_gateway.service_domain_name
    }
}

resource "aws_s3_bucket_notification" "batch_processing_source_lambda_trigger" {
    bucket = aws_s3_bucket.batch_data_source_bucket.id
    lambda_function {
        lambda_function_arn = module.batch_processing.lambda_arn
        events              = ["s3:ObjectCreated:*"]
    }
    depends_on = [aws_lambda_permission.allow_terraform_bucket]
}
resource "aws_lambda_permission" "allow_terraform_bucket" {
    statement_id  = "AllowExecutionFromS3Bucket"
    action        = "lambda:InvokeFunction"
    function_name = module.batch_processing.lambda_arn
    principal     = "s3.amazonaws.com"
    source_arn    = aws_s3_bucket.batch_data_source_bucket.arn
}
