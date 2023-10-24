variable "prefix" {}
variable "short_prefix" {}
variable "zone_id" {}
variable "api_domain_name" {}
variable "environment" {}
variable "oas" {}

variable "routes" {
    type = list(object({
        function_name : string
    }))
}
