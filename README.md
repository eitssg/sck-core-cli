#  SCK Module - CORE

# REMODELING THIS LIBRARY.  IT IS STILL DRAFT

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

## Installation

```bash
# python -m venv .venv
# source .venv/bin/activate
# pip install simple-cloud-kit
# core --help
  Simple Cloud Kit (c) 2024 Exclusive Information Technology Service
  Core 0.0.1-pre01934jf
  ...help text (coming soon!!!)
```

## Setup / Contributing

### Setup

#### step 1

Clone the repositry:

```bash
git clone https://github.com/etissg/simple-cloud-kit.git
cd simple-cloud-kit
python -m venv .venv
```
There are 14 git submodules in this repo.  Sync all the submodules and pull all the subprojects

#### step 2

In IntelliJ or VSCode, select this python as the interpreter.  

Next, evaluate the build tool scripts for windwos (.ps1) powershell, or linux (.sh) bash (not zsh or sh...bash)

In vsCode or Intellij, add each of the 14 submoduels to the workspace.

run "build-all.sh" to install and build all submodules and install all dependencies

```bash
source ./build-all.sh
```

Talk to me via Github (jbarwick@eits.com.sg)
