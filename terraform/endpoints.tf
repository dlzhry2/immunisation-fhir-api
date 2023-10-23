/// This file creates all lambdas needed for each endpoint plus api-gateway

locals {
    policy_path = "${path.root}/policies"
}

data "aws_iam_policy_document" "logs_policy_document" {
    source_policy_documents = [templatefile("${local.policy_path}/log.json", {} )]
}
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

locals {
    imms_endpoints = [
        "get_imms", "create_imms", "search_imms"
    ]
    imms_table_name      = aws_dynamodb_table.test-dynamodb-table.name
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
        for lambda in module.imms_event_endpoint_lambdas[*] : lambda.function_name =>
        { invoke_arn : lambda.invoke_arn, lambda_arn : lambda.lambda_arn }
    }

}
output "debug_lambdas" {
    value = local.imms_lambdas
}

locals {
    oas_parameters = {
        get_event = local.imms_lambdas["${local.short_prefix}_get_imms"]

    }
    oas = templatefile("${path.root}/oas.yaml", local.oas_parameters)
}
output "oas" {
    value = local.oas
}

module "api_gateway" {
    source = "./api_gateway3"

    prefix          = local.prefix
    short_prefix    = local.short_prefix
    zone_id         = data.aws_route53_zone.project_zone.zone_id
    api_domain_name = local.service_domain_name
    environment     = local.environment
    oas             = local.oas
}

#resource "aws_lambda_permission" "api_gw" {
#    count         = length(module.imms_event_endpoint_lambdas[*])
#    statement_id  = "AllowExecutionFromAPIGateway"
#    action        = "lambda:InvokeFunction"
#    function_name = var.routes[count.index].function_name
#    principal     = "apigateway.amazonaws.com"
#    source_arn    = "${aws_apigatewayv2_api.service_api.execution_arn}/*/*"
#}


