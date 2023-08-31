resource "aws_s3_bucket" "test_bucket" {
  bucket        = "${local.prefix}-test-bucket"
  force_destroy = true
}
