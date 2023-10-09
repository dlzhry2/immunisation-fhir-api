data "aws_caller_identity" "current" {}
data "archive_file" "catch_all_lambda_archive" {
  type        = "zip"
  source_dir  = "../${path.module}/src"
  output_path = "build/catch_all_lambda_function_code.zip"
}

output "lambda_build_path_output" {
  value = "../${path.module}/src"
}

resource "null_resource" "catch_all_lambda_dist" {
  triggers = {
    token_validator_src = data.archive_file.catch_all_lambda_archive.output_sha
  }

  provisioner "local-exec" {
    interpreter = ["bash", "-c"]

    command = <<EOF
  aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.eu-west-2.amazonaws.com
  # Create a dist folder and copy only the js files to distribution.
  # AWS Lambda does not have a use for a package.json or typescript files on runtime.
  mkdir -p ../catch_all_lambda/dist &&\
  cp -r ../catch_all_lambda/src/catch_all_lambda.py ../catch_all_lambda/dist &&\
  cd ../catch_all_lambda/dist &&\
  find . -name "*.zip" -type f -delete && \
  #Create zips directory under terraform, delete existing one
  mkdir -p ../../terraform/zips && \
  # Zip everything in the dist folder and move to terraform directory
  # cd ../../terraform/
  # zip -r ../../terraform/zips/$(terraform output catch_all_lambda_zip_name).zip .
  zip -r ../../terraform/zips/catch_all_lambda_function_code.zip . && \
  #Delete Distibution folder
  cd .. && rm -rf dist/
  aws s3 cp ../terraform/zips/catch_all_lambda_function_code.zip s3://${aws_s3_bucket.catch_all_lambda_bucket.bucket}/catch_all_lambda_function_code.zip
   EOF
       
  }
}