module "batch_processing" {
    source = "./batch_processing"
    prefix = local.prefix
    vpc_id = "vpc-0d0eff78ca2280e19"
}
