    

  # Create a dist folder and copy only the js files to distribution.
  # AWS Lambda does not have a use for a package.json or typescript files on runtime.
  mkdir -p ../catch_all_lambda/dist &&\
  cp -r ../catch_all_lambda/src/catch_all_lambda.py ../catch_all_lambda/dist &&\
  cd ../catch_all_lambda/dist &&\
  find . -name "*.zip" -type f -delete && \
  #Create zips directory under terraform, delete existing one
  mkdir -p ../../terraform/zips && \
  # Zip everything in the dist folder and move to terraform directory
  zip -r ../../terraform/zips/catch_all_lambda_function_code.zip . && \
  #Delete Distibution folder
  cd .. && rm -rf dist