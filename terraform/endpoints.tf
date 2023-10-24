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

        "get_imms", "create_imms", "search_imms", "delete_imms"
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
    # Mapping outputs with each called lambda
     imms_lambdas = {
    for lambda in module.imms_event_endpoint_lambdas[*] : lambda.function_name =>
    {
      lambda_arn : lambda.lambda_arn
    }
  }

#Constructing routes for API Gateway
 routes = [
    for lambda_name,lambda_attr in local.imms_lambdas : {
      function_name = lambda_name
    }
  ]
}
output "debug_lambdas" {
    value = local.imms_lambdas
}
output "debug_lambdas2" {
    value = local.routes
}

locals {
    oas_parameters = {
        get_event = local.imms_lambdas["${local.short_prefix}_get_imms"]
        post_event= local.imms_lambdas["${local.short_prefix}_create_imms"]

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
    routes = local.routes
}
