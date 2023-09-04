resource "aws_s3_bucket" "lambda_bucket" {
  bucket        = "${var.prefix}-lambda-bucket"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "versioning_lambda_bucket" {
  bucket = aws_s3_bucket.lambda_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}