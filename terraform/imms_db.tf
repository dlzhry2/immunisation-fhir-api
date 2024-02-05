resource "aws_dynamodb_table" "test-dynamodb-table" {
    name         = "${local.short_prefix}-imms-events"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "PK"

    attribute {
        name = "PK"
        type = "S"
    }
    attribute {
        name = "PatientPK"
        type = "S"
    }
    attribute {
        name = "PatientSK"
        type = "S"
    }
    attribute {
        name = "Identifier"
        type = "S"
    }

    global_secondary_index {
        name               = "PatientGSI"
        hash_key           = "PatientPK"
        range_key          = "PatientSK"
        projection_type    = "ALL"
    }

    global_secondary_index {
        name               = "IdentifierGSI"
        hash_key           = "Identifier"
        projection_type    = "ALL"
    }
}
