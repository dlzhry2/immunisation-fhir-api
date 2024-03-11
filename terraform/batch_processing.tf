module "batch_processing" {
    source = "./batch_processing"
    prefix = local.prefix
    vpc_id = var.default_vpc_id
}
