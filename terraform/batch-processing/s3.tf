resource "aws_s3_bucket" "source" {
    bucket = "source"
}

resource "aws_s3_bucket" "destination" {
    bucket = "destination"
}
