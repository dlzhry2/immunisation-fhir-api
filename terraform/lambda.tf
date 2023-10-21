locals {
    lambda_dir         = abspath("${path.root}/../lambda_code")
    build_dir          = abspath("${path.root}/build")
    # lambda_source_zip is only used for change detection. lambda_deployment_zip is the final zip file that is getting deployed
    lambda_source_zip  = "lambda_source_code.zip"
    lambda_package_zip = "${local.build_dir}/lambda_package.zip"
}

data "archive_file" "lambda_source_zip" {
    type        = "zip"
    source_dir  = "${local.lambda_dir}/src"
    output_path = "${local.build_dir}/${local.lambda_source_zip}"
}
locals {
    lambda_code_sha = data.archive_file.lambda_source_zip.output_base64sha256
}

resource "aws_s3_bucket" "lambda_source_bucket" {
    bucket        = "${local.prefix}-lambda-source-code"
    force_destroy = true
}

resource "null_resource" "lambda_package" {
    triggers = {
        lambda_source_code = local.lambda_code_sha
        docker_file        = filemd5("${local.lambda_dir}/Dockerfile")
        entrypoint         = filemd5("${local.lambda_dir}/entrypoint.sh")
    }

    provisioner "local-exec" {
        interpreter = ["bash", "-c"]
        command     = <<EOF
docker build -f ${local.lambda_dir}/Dockerfile -t ${local.prefix}-lambda-build ${local.lambda_dir}
docker run --rm -v ${local.build_dir}:/build ${local.prefix}-lambda-build
   EOF
    }
}
resource "aws_s3_object" "lambda_function_code" {
    bucket      = aws_s3_bucket.lambda_source_bucket.bucket
    key         = "package"
    source      = local.lambda_package_zip
    source_hash = local.lambda_code_sha
    depends_on  = [null_resource.lambda_package]
}

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

