#!/usr/bin/python3
"""
Example usage:
From core-automation/lambdas/component_compiler
$ ./cli.py -c sia -p core -a network -b master -n 1 --mode local --app-path ../../../core-network/
Then check core-network/_compiled/deploy.actions
"""
import os
import re
import yaml
import argparse
import json


import core_deployspec_compiler.handler as lambda_function


def __to_yaml(object):
    """Some sane defaults."""
    return yaml.safe_dump(
        object,
        default_flow_style=False,
        width=1000,
        # default_style='"'
    )


def _get_args():
    parser = argparse.ArgumentParser(
        description="Deployspec Compiler for the Action Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-s", "--scope", help="Scope name", required=False)
    parser.add_argument(
        "-c", "--client", help="Client name for selecting config", required=True
    )
    parser.add_argument("-p", "--portfolio", help="Portfolio name", required=True)
    parser.add_argument("-a", "--app", help="Application name", required=True)
    parser.add_argument("-b", "--branch", help="Branch name", required=True)
    parser.add_argument(
        "-n", "--build", help="Build number", required=True
    )  # Defaults to 1?
    parser.add_argument(
        "--mode", default=None, help="Mode of operation (default|local)"
    )
    parser.add_argument(
        "--app-path", default=None, help="Local app path (local mode only)"
    )
    parser.add_argument(
        "--aws-profile",
        help="Select which profile to use from your ~/.aws/credentials file.",
    )
    parser.add_argument("--client-vars", help="Client vars")
    parser.add_argument(
        "--bucket-region", default="ap-southeast-1", help="S3 Bucket Region"
    )
    parser.add_argument("--bucket-name", default=None, help="S3 Bucket Name")
    parser.add_argument("--s3-facts-prefix", default=None, help="S3 facts prefix")

    args = parser.parse_args()

    scope_prefix = "{}-".format(args.scope) if args.scope is not None else ""
    if args.bucket_name is None:
        args.bucket_name = "{}{}-core-automation-{}".format(
            scope_prefix, args.client, args.bucket_region
        )

    return args


def run(args):
    """Run deployspec compiler locally, using content from s3."""

    # Load client vars and set into env.
    client_vars_file = "../../../{}-config/client-vars.yaml".format(args.client)
    if args.client_vars is not None:
        client_vars_file = args.client_vars
    with open(client_vars_file) as f:
        client_vars = yaml.safe_load(f.read())
    for key in client_vars:
        os.environ[key] = "{}".format(client_vars[key])
    print("client_vars:\n{}".format(__to_yaml(client_vars)))

    accounts_file = "../{}-config/accounts.yaml".format(args.client)
    print("account file name ", accounts_file)
    print("Current Directory", os.getcwd())
    print("List subdirectories in the directory")
    os.listdir("../")

    portfolio_name = args.portfolio + "-" + args.branch
    print("Portfolio-name", portfolio_name)
    tags = {}
    if os.path.exists(accounts_file):
        with open(accounts_file) as f:
            client_accounts_file = yaml.safe_load(f.read())
        portfolio_name = args.portfolio + "-" + args.branch
        print("Portfolio-name", portfolio_name)
        if portfolio_name in client_accounts_file:
            block_data = client_accounts_file[portfolio_name]
            print("block_data", block_data)

            if "Tags" in block_data.get("AccountFacts", {}):
                tags = block_data["AccountFacts"]["Tags"]
                print("Tags from Accounts.yaml", tags)

    if args.aws_profile is not None:
        print("Setting AWS_PROFILE={}".format(args.aws_profile))
        os.environ["AWS_PROFILE"] = args.aws_profile

    if args.mode == "local" and args.app_path is None:
        raise ValueError("Must have app_path is mode=local.")

    branch_short_name = re.sub(r"[^a-z0-9\\-]", "-", args.branch.lower())[0:20].rstrip(
        "-"
    )

    event = {
        "Package": {
            "BucketName": args.bucket_name,
            "BucketRegion": args.bucket_region,
            "Key": "packages/{}/{}/{}/{}/package.zip".format(
                args.portfolio, args.app, args.branch, args.build
            ),
            "VersionId": None,
            "Mode": args.mode,
            "AppPath": args.app_path,
        },
        "DeploymentDetails": {
            "Portfolio": args.portfolio,
            "App": args.app,
            "Branch": args.branch,
            "BranchShortName": branch_short_name,
            "Build": args.build,
            "Tags": tags,
        },
    }

    print("cli invoke event:\n{}".format(__to_yaml(event)))
    response = lambda_function.handler(event, {})
    print("cli handler response:\n{}".format(__to_yaml(response)))

    response_string = json.dumps(response, indent=4, sort_keys=True)

    f = open("compile-response.txt", "w")
    f.write(response_string)
    f.close()


# Use this pattern
if __name__ == "__main__":
    args = _get_args()
    run(args)
