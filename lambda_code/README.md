# immunisation-fhir-api lambda

## Setup for local dev

The tests are in a separate module so in order for them to see each other we need to let the IDE know about the relationship.

### IntelliJ

- Open the root repo directory in IntelliJ.
- Set up the interpreter as you see fit.
  - One option is direnv and pyenv with an `.envrc` of `layout pyenv 3.8.10`.  
    Then add an existing virtualenv SDK in the project settings for `.direnv/python-3.8.10/bin/python`
- Add a new module of the `lambda_code` directory to the Project Structure. Add the `src` and `tests` directories as sources.


### VS Code

- Add the `src` directory as an additional analysis path.  
  `.vscode/settings.json`:  
    ```
    "python.analysis.extraPaths": [
        "./lambda_code/src"
    ]
    ```
- Run the `Python: Configure Tests` command and when it asks for a directory give it `lambda_code`.
