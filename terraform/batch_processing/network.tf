locals {
    subnets = [
        {
            cidr              = "10.0.0.0/16"
            is_public         = true
            availability_zone = "eu-west-2a"
        }
    ]
}

resource "aws_subnet" "subnet" {
    count                   = length(local.subnets)
    cidr_block              = local.subnets[count.index].cidr
    vpc_id                  = var.vpc_id
    availability_zone       = local.subnets[count.index].availability_zone
    map_public_ip_on_launch = local.subnets[count.index].is_public

    tags = {
        Name = "${var.prefix}-${local.subnets[count.index].is_public ? "public" : "private"}-${local.subnets[count.index].availability_zone}"
    }
}

resource "aws_security_group" "service_security_group" {
    name   = "${var.prefix}-task"
    vpc_id = var.vpc_id

    egress {
        protocol    = "-1"
        from_port   = 0
        to_port     = 0
        cidr_blocks = ["0.0.0.0/0"]
    }

    #    ingress {
    #        protocol    = "tcp"
    #        from_port   = var.container_port
    #        to_port     = var.container_port
    #        cidr_blocks = data.aws_subnet.private_subnets.*.cidr_block
    #    }
}
