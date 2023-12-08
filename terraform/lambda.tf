locals {
    lambda_dir         = abspath("${path.root}/../lambda_code")
    #build_dir          = abspath("${path.root}/build")
    # lambda_source_zip is only used for change detection. lambda_deployment_zip is the final zip file that is getting deployed
    #lambda_source_zip  = "lambda_source_code.zip"
    #lambda_package_zip = "${local.build_dir}/lambda_package.zip"

    source_path   = local.lambda_dir
    path_include  = ["**"]
    path_exclude  = ["**/__pycache__/**"]
    files_include = setunion([for f in local.path_include : fileset(local.source_path, f)]...)
    files_exclude = setunion([for f in local.path_exclude : fileset(local.source_path, f)]...)
    files         = sort(setsubtract(local.files_include, local.files_exclude))

    dir_sha = sha1(join("", [for f in local.files : filesha1("${local.source_path}/${f}")]))
}

/*data "archive_file" "lambda_source_zip" {
    type        = "zip"
    source_dir  = "${local.lambda_dir}/src"
    output_path = "${local.build_dir}/${local.lambda_source_zip}"
}
locals {
    lambda_code_sha = data.archive_file.lambda_source_zip.output_base64sha256
}*/
/*
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
}*/

#resource "docker_image" "lambda_function_docker" {
module "docker_image" {
    source = "terraform-aws-modules/lambda/aws//modules/docker-build"

    create_ecr_repo = true
    ecr_repo        = "${local.prefix}-lambda-repo"
    ecr_repo_lifecycle_policy = jsonencode({
        "rules" : [
            {
                "rulePriority" : 1,
                "description" : "Keep only the last 2 images",
                "selection" : {
                    "tagStatus" : "any",
                    "countType" : "imageCountMoreThan",
                    "countNumber" : 2
                },
                "action" : {
                    "type" : "expire"
                }
            }
        ]
    })

    use_image_tag = false
    #image_tag     = "1.0"

    source_path      = local.lambda_dir

    triggers = {
/*        lambda_source_code = local.lambda_code_sha
        docker_file        = filemd5("${local.lambda_dir}/Dockerfile-poetry")
        dir_sha1           = sha1(join("", [for f in fileset(path.module, "src*//*") : filesha1(f)]))*/
        dir_sha = local.dir_sha
    }
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
data "aws_ecr_authorization_token" "token" {}

provider "docker" {
    registry_auth  {
        address  = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com"
        username = data.aws_ecr_authorization_token.token.user_name
        password = data.aws_ecr_authorization_token.token.password
    }
}
