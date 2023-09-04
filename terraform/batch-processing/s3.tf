resource "aws_s3_bucket" "source" {
    bucket = "${var.prefix}-batch-lambda-source"
}

resource "aws_s3_bucket" "destination" {
    bucket = "${var.prefix}-batch-lambda-destination"
}
