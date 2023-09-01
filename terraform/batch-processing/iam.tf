resource "aws_iam_role" lambda_role {
  name = "${var.short_prefix}-lambda-role"
  assume_role_policy = <<EOF
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": [
            "sts:AssumeRole",
            "s3:DeleteObject",
            "s3:ListBucket",
            "s3:HeadObject",
            "s3:GetObject",
            "s3:GetObjectVersion",
            "s3:PutObject"
          ],
          "Principal": {
            "Service": "lambda.amazonaws.com"
          },
          "Effect": "Allow",
          "Sid": ""
        }
      ]
    }
    EOF
}

resource aws_iam_role_policy_attachment lambda {
  role = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "apig_lambda_policy" {
  statement {
    actions = [
      "lambda:InvokeFunction",
    ]
    effect    = "Allow"
    resources = [aws_lambda_function.batch_processing_lambda.arn]
    sid       = "ApiGatewayInvokeLambda"
  }
}

data "aws_iam_policy_document" "apig_lambda_role_assume" {
  statement {
    actions = [
      "sts:AssumeRole",
      "s3:DeleteObject",
      "s3:ListBucket",
      "s3:HeadObject",
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:PutObject"
    ]
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "apig_lambda_role" {
  name               = "${var.short_prefix}-apig-authorize-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.apig_lambda_role_assume.json
}

resource "aws_iam_policy" "apig_lambda" {
  name   = "${var.short_prefix}-apig-lambda-policy"
  policy = data.aws_iam_policy_document.apig_lambda_policy.json
}

resource "aws_iam_role_policy_attachment" "apig_lambda_role_to_policy" {
  role       = aws_iam_role.apig_lambda_role.name
  policy_arn = aws_iam_policy.apig_lambda.arn
}
