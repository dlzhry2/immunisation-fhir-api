locals {
    api_routes = [
        {
            path : "/event", verb : "GET", function_name : "imms-jaho3_get_imms",
            invoke_arn : "arn:aws:apigateway:eu-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-2:790083933819:function:imms-jaho3_get_imms/invocations"
        }
    ]
}
module "api_gateway" {
    source = "./api_gateway2"

    prefix          = local.prefix
    short_prefix    = local.short_prefix
    zone_id         = data.aws_route53_zone.project_zone.zone_id
    api_domain_name = local.service_domain_name
    environment     = local.environment
    routes          = local.api_routes
}
