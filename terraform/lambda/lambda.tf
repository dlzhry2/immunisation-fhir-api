/*resource "aws_lambda_function" "lambda" {
    role          = aws_iam_role.lambda_role.arn
    timeout       = 300
    #s3_bucket     = var.source_bucket
    #s3_key        = var.source_key
    function_name = "${var.short_prefix}_${var.function_name}"
    handler       = "${var.function_name}_handler.${var.function_name}_handler"
    runtime       = "python3.9"
    #package_type  = "Image"

    #source_code_hash = var.source_sha

    create_package = false
    image_uri     = var.image_uri
    package_type  = "Image"
    architectures = ["x86_64"]

    environment {
        variables = var.environments
    }
}*/


module "lambda_function_container_image" {
    source = "terraform-aws-modules/lambda/aws"

    create_role = false
    lambda_role = aws_iam_role.lambda_role.arn
    function_name = "${var.short_prefix}_${var.function_name}"
    handler       = "${var.function_name}_handler.${var.function_name}_handler"

    create_package = false
    image_uri    = var.image_uri
    package_type = "Image"
    architectures = ["x86_64"]

    environment_variables = var.environments
    image_config_command = ["${var.function_name}_handler.${var.function_name}_handler"]
}
