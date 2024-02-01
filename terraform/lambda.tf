locals {
    lambda_dir    = abspath("${path.root}/../lambda_code")
    source_path   = local.lambda_dir
    path_include  = ["**"]
    path_exclude  = ["**/__pycache__/**"]
    files_include = setunion([for f in local.path_include : fileset(local.source_path, f)]...)
    files_exclude = setunion([for f in local.path_exclude : fileset(local.source_path, f)]...)
    files         = sort(setsubtract(local.files_include, local.files_exclude))

    dir_sha = sha1(join("", [for f in local.files : filesha1("${local.source_path}/${f}")]))
}

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

    platform = "linux/amd64"
    use_image_tag = false
    source_path   = local.lambda_dir
    triggers = {
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
