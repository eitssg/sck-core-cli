#  SCK Module - CORE

Thie CORE module is the primary interface files.  It's intent is to replace
these commands:

* associate-hosted-zones-to-vpcs.py
* clean-lambda-dependencies.py
* clean-s3-app-branch.py
* delete-default-vpcs.py
* deploy-custom-resource-handler.sh
* deploy.sh
* describe_stack.py
* find-appspec-stacks.py
* find-compiling-components.py
* find-git-pulls.py
* install-lambda-dependencies.py
* migrate-api-db.py
* print_deployment_status.py
* run-local.sh
* run-v2.sh
* run.sh
* set-iam-password-policy.py
* teardown-failed-stacks.py
* teardown.sh

On the commandline you will first type in 'core' followed by command:

Usage: core [command] [<tasks>] [<actions>] [<options>]

| command   | task     | action     | description                                                                                                                                             |
| --------- | -------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| configure |          |            | Configure Client Vars                                                                                                                                   |
| engine    | zones    | associate  | Ensure all zones are registered as private zones in Route53                                                                                             |
| engine    | zones    | verify     | Verify all zones and print any anomolies                                                                                                                |
| engine    | clean    |            | Delete everything from S3 and start LZ's from scratch                                                                                                   |
| engine    | vpc      | default    | Manage default VPC's in all zones listed in the account registry                                                                                        |
| engine    | init     | all        | Initialize the Core platform and deploy things such as the custom resource handler                                                                      |
| engine    | init     | resources  | Deploys common CloudFormation Resources                                                                                                                 |
| engine    | deploy   | all        | Deploys Everything (except codecommit)                                                                                                                  |
| engine    | deploy   | invoker    | Deploy/Update the invoker                                                                                                                               |
| engine    | deploy   | runner     | Deploy/Update the runner ( step functions )                                                                                                             |
| engine    | deploy   | compiler   | Deploy/Update the compiler                                                                                                                              |
| engine    | deploy   | api-legacy | Deploy/Update the old API                                                                                                                               |
| engine    | deploy   | api-lambda | Deploy/Update the lambda API                                                                                                                            |
| engine    | deploy   | api-db     | Deploy the Databases required for ALL other functions (do this first)                                                                                   |
| engine    | deploy   | codecommit | Deploy the codecommit services.                                                                                                                         |
| engine    | deploy   | facts      | Deploy the facts YAML files into S3 and update the DynamoDB tables core-client-table, core-portfolio-table, core-accounts-table, core-apps-table        |
| engine    | app      | describe   | Reads JSON file from [stdin] and generates a stack description                                                                                          |
| engine    | app      | find       | Scan cloudformation stacks and build up a nested dictionary of names, typically portfolio-app-branch                                                    |
| engine    | app      | components | Search cloudwatch logs for compiler to identify Consumables in use                                                                                      |
| engine    | app      | status     | Get the status of a deploying app (CloudFormation Status)                                                                                               |
| engine    | source   | pulls      | Search CloudTrail for core-automation GitPull events                                                                                                    |
| engine    | migrate  |            | API DB migration                                                                                                                                        |
| engine    | teardown |            | Remove Core Automation CloudFormation Stacks, Databases, and S3 Buckets                                                                                 |
| run       | apply    |            | Apply an Application Changeset (CloudFormation or Terraform Apply)                                                                                      |
| run       | compile  |            | Compile a deploypec or appspec or terraform template and runs linters and validators                                                                    |
| run       | deploy   |            | Deploy an Application (CloudFormation create/update or terrform plan/apply)                                                                             |
| run       | package  |            | An optional stage to run a standard python or node packager on lambda deployments.  Typically in CI pipelines, not CD Pipelines                         |
| run       | plan     |            | Create an Appicaton Changeset (CloudFormation Changeset or Terraform Plan)                                                                              |
| run       | release  |            | Update DNS servers to point to a specific deployment instance.  If not in the DynamoDB or in the wrong state, this will fail                            |
| run       | show     |            | Show and describe a specific infrastructure deployment.  CloudFormaton or Terraform describe                                                            |
| run       | upload   |            | Upload deployment artefacts in the "files" folder into the proper S3 bucket for deployment.  This is a MUST else compile plan, apply, deploy will fail  |
| run       | teardown |            | Teardown an instance of the depoyment.  CloudFormation application or Terraform state file.  Ensures the stack or tfstate is deleted from all databases |

The above commands replace the core-automation/bin shell scripts and python scripts into this "core" deployment object.

This object is installed with:

```bash
# python -m pip install sck-mod-core
# core --help
  Simple Cloud Kit (c) 2024 EITS
  Core Module v1.2
  ...help text
```

If you also have the sck installed, core can be called from the sck command line

```bash
# python -m pip install simple-cloud-kit
# sck core --help
  Simple Cloud Kit (c) 2024 EITS
  Core Module v1.2
  ...help text
```

## Setup / Contributing

### Setup

#### step 1

We will create a venv in the parent folder and then you will need to use this as the python interpreter.

In this folder, we have told *pyenv* that we wish to use python 3.12.3

From the sck-mod-core folder
```shell
python -m venv ../venv
```

#### step 2

In IntelliJ or VSCode, select this python as the interpreter.  Once done, run activate the environment and
run the poetry_setup.sh shell script.

```shell
source ../venv/bin/activate
source poetry_setup.sh
```

#### Scripts

*associate-hosted-zones-to-vpcs.py*
Finds and associates private hosted zones to services VPCs.

*delete-default-vpcs.py*
Deletes the defalut VPC from a list of accounts and regions.

*deploy-core-automation-resources.sh*
Deploys the core-automation-resources.yaml stack to every listed account. This is required during inital account bootstrapping to provide the action runner appropriate access to each sub account.

*deploy-runner.sh*
Deploys the action runner using CloudFormation

*deploy-invoker.sh*
Deploys the S3 invoker Lambda using CloudFormation

*install-lambda-dependencies.py*
Installs pip packages and copies over common packages for each Lambda function in /lambdas

    * Performs a pip install of all packages listed in /lambdas/<function>/lib/pip.txt
    * Copies common package for all packages listed in /lambdas/<function>/lib/common.txt
    * Common packages are stored in /lambdas/_common (deprecated) will be moved to /core-framework/ as a python module.  This module should be added to the requirements.txt for each lambda function.
    *

Run this before deploying to AWS
