-include .env

interactionId=$(environment)

aws_profile = apim-dev
tf_cmd = AWS_PROFILE=$(aws_profile) terraform

project_name = immunisation
project_short_name = imms
state_bucket = $(project_name)-terraform-state
tf_state= -backend-config="bucket=$(state_bucket)"

tf_vars= -var="project_name=$(project_name)" -var="project_short_name=$(project_short_name)"

workspace:
	$(tf_cmd) workspace new $(environment) || $(tf_cmd) workspace select $(environment) && echo "Switched to workspace/environment: $(environment)"

init:
	$(tf_cmd) init $(tf_state) $(tf_vars) 

plan: workspace
	 $(tf_cmd) plan $(tf_vars) 

apply: workspace
	$(tf_cmd) apply $(tf_vars) -auto-approve

clean:
	rm -rf build .terraform upload-key

destroy: workspace
	$(tf_cmd) destroy $(tf_vars) -auto-approve 
	teraform workspace select default
	terraform workspace delete $(environment)

output:
	$(tf_cmd) output -raw $(name)
