resource "aws_dynamodb_table" "test-dynamodb-table" {
    name         = "${local.short_prefix}-imms-events"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "PK"

    attribute {
        name = "PK"
        type = "S"
    }
}

