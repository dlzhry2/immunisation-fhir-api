resource "aws_dynamodb_table" "delta-dynamodb-table" {
    name         = "${local.short_prefix}-delta-logs"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "Operation"
    range_key = "DateTimeStamp"

    attribute {
        name = "DateTimeStamp"
        type = "S"
    }
    attribute {
        name = "Operation"
        type = "S"
    }  
}


