locals {
    lambda_source_dir     = "${path.root}/../lambda_code"
    build_dir             = "build"
    # lambda_source_zip is only used for change detection. lambda_deployment_zip is the final zip file that is getting deployed
    lambda_source_zip     = "lambda_source_code.zip"
    lambda_deployment_zip = "lambda_deployment.zip"
}

data "archive_file" "lambda_source_zip" {
    type        = "zip"
    source_dir  = local.lambda_source_dir
    output_path = "${local.build_dir}/${local.lambda_source_zip}"
}

resource "aws_s3_bucket" "lambda_deployment" {
    bucket        = "${local.prefix}-lambda-source-code"
    force_destroy = true
}

resource "null_resource" "lambda_install_dependencies" {
    triggers = {
        lambda_source_code = data.archive_file.lambda_source_zip.output_sha
    }

    provisioner "local-exec" {
        interpreter = ["bash", "-c"]
        command     = <<EOF

cd "${path.root}"
build_dir="${path.root}/${local.build_dir}/lambda"
mkdir -p $build_dir
cd $build_dir

cp -r "${abspath(local.lambda_source_dir)}/" .
pip install -r requirements.txt --target .

zip -r "../${local.lambda_deployment_zip}" .
   EOF
    }
}

locals {
    lambda_deployment_path = "${path.root}/${local.build_dir}/${local.lambda_deployment_zip}"
    lambda_bucket_key      = "package"
}

data "local_file" "deployment_code" {
    filename   = local.lambda_deployment_path
    depends_on = [null_resource.lambda_install_dependencies]
}

resource "aws_s3_object" "lambda_function_code" {
    bucket = aws_s3_bucket.lambda_deployment.bucket
    key    = local.lambda_bucket_key
    source = local.lambda_deployment_path
    etag   = data.local_file.deployment_code.content_md5
}

locals {
    policy_path = "${path.root}/policies"
}

data "aws_iam_policy_document" "logs_policy_document" {
    source_policy_documents = [templatefile("${local.policy_path}/log.json", {} )]
}
locals {
    endpoint_dynamodb_env_vars = {
        "DYNAMODB_TABLE_NAME" = module.dynamodb.dynamodb_table_name
    }
}

module "get_status" {
    source        = "./lambda2"
    prefix        = local.prefix
    short_prefix  = local.short_prefix
    function_name = "get_status"
    source_bucket = aws_s3_bucket.lambda_deployment.bucket
    source_key    = aws_s3_object.lambda_function_code.key
    source_etag   = data.archive_file.lambda_source_zip.output_sha
    policy_json   = data.aws_iam_policy_document.logs_policy_document.json
}

data "aws_iam_policy_document" "endpoint_policy_document" {
    source_policy_documents = [
        templatefile("${local.policy_path}/dynamodb.json", {
            "dynamodb_table_name" : module.dynamodb.dynamodb_table_name
        } ),
        templatefile("${local.policy_path}/log.json", {} ),
    ]
}
module "get_event" {
    source        = "./lambda2"
    prefix        = local.prefix
    short_prefix  = local.short_prefix
    function_name = "get_event"
    source_bucket = aws_s3_bucket.lambda_deployment.bucket
    source_key    = aws_s3_object.lambda_function_code.key
    source_etag   = data.archive_file.lambda_source_zip.output_sha
    policy_json   = data.aws_iam_policy_document.endpoint_policy_document.json
    environments  = local.endpoint_dynamodb_env_vars
}
