// This file creates all lambdas needed for each endpoint, except /_status
locals {
    imms_table_name = aws_dynamodb_table.test-dynamodb-table.name
    imms_endpoints  = [
        "get_imms", "create_imms", "search_imms"
    ]
    imms_lambda_env_vars = {
        "DYNAMODB_TABLE_NAME" = local.imms_table_name
    }
}

data "aws_iam_policy_document" "imms_policy_document" {
    source_policy_documents = [
        templatefile("${local.policy_path}/dynamodb.json", {
            "dynamodb_table_name" : local.imms_table_name
        } ),
        templatefile("${local.policy_path}/log.json", {} ),
    ]
}

module "imms_event_endpoint_lambdas" {
    source = "./lambda"
    count  = length(local.imms_endpoints)

    prefix        = local.prefix
    short_prefix  = local.short_prefix
    function_name = local.imms_endpoints[count.index]
    source_bucket = aws_s3_bucket.lambda_source_bucket.bucket
    source_key    = aws_s3_object.lambda_function_code.key
    source_sha    = aws_s3_object.lambda_function_code.source_hash
    policy_json   = data.aws_iam_policy_document.imms_policy_document.json
    environments  = local.imms_lambda_env_vars
}

locals {
    imms_lambdas = {
        for lambda in module.imms_event_endpoint_lambdas[*] : lambda.function_name =>{ invoke_arn : lambda.invoke_arn }
    }

}
output "imms_l" {
    value = local.imms_lambdas
}
