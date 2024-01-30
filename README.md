# immunisation-fhir-api

See `README.specification.md` for details of the API specification's development.


## Directories

```
lambda_code - The API code.
terraform   - Infrastructure.
tests       - Integration tests.
devtools    - Helper project for development.
```

See any readmes in those directories for more details.


## Spelling

Refer to the FHIR Immunization resource capitalised and with a "z" as FHIR is U.S. English.

All other uses are as British English i.e. "immunisation".

See https://nhsd-confluence.digital.nhs.uk/display/APM/Glossary.


## Setup for local dev

`lambda_code` should have its own environment to keep it separate from the infrastructure and integration tests.

### Tools

Install `direnv` and `pyenv`.
https://direnv.net/docs/installation.html
https://github.com/pyenv/pyenv?tab=readme-ov-file#installation

These tools automate the Python version and environment creation and use, and selects them automatically when entering a directory.  
`pyenv` separates Python versions and `direnv` handles the environment.
`direnv` uses `pyenv` to select the version and creates an environment under `.direnv/`.


### Install Python versions and environments

Run `make setup-python-envs`

This will set up everything up for both the root and `lambda_code`.


### IDEs

The tests are in a separate module so in order for them to see each other we need to let the IDE know about the relationship.

#### IntelliJ

- Open the root repo directory in IntelliJ.
- In Project Structure add an existing virtualenv SDK for `.direnv/python-x.x.x/bin/python`.
- Set the project SDK and the default root module SDK to the one created above.
  - Add `src` and `tests` as sources.
  - Add `.direnv` and `terraform` as exclusions if they're not already.
- Add another existing virtualenv SDK for `lambda_code/.direnv/python-x.x.x/bin/python`.
- Import a module pointed at the `lambda_code` directory, set the SDK created above.
  - Add the `src` and `tests` directories as sources.
  - Add `.direnv` as an exclusion if it's not already.


#### VS Code

The project must be opened as a multi-root workspace for VS Code to know that `lambda_code` has its own environment.

- Open the workspace `immunisation-fhir-api.code-workspace`.
- Copy `lambda_code/.vscode/settings.json.default` to `lambda_code/.vscode/settings.json`, or merge the contents with your existing file.
- Run the `Python: Configure Tests` command. Select the `lambda_code` workspace, then `unittest`, then `.`.

