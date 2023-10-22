variable "prefix" {}
variable "short_prefix" {}
variable "zone_id" {}
variable "api_domain_name" {}
variable "environment" {}

variable "routes" {
    type = list(object({
        path : string,
        verb : string,
        function_name : string,
        invoke_arn : string
    }))
}
