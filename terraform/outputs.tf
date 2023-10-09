output "service_domain_name" {
  value = module.api_gateway.service_domain_name
}

output "catch_all_lambda_path_output" {
  value = module.catch_all_lambda.catch_all_lambda_path_output
}

output "catch_all_lambda_source_file" {
  value = module.catch_all_lambda.catch_all_lambda_source_file
}