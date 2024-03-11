locals {
    batch_processing_source_dir = "${path.module}/task_code"
}

module "docker_image" {
    source = "terraform-aws-modules/lambda/aws//modules/docker-build"

    create_ecr_repo           = false
    ecr_repo                  = aws_ecr_repository.batch_processing_repository.name
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

    platform      = "linux/amd64"
    use_image_tag = false
    source_path   = local.batch_processing_source_dir
    triggers      = {
        dir_sha = uuid()
    }
}

