""" Manage the organization accounts """

import os
import boto3
from botocore.exceptions import ClientError

from .user import execute_user, add_user_parser


def _assume_role(profile, account_id, role_name):
    """rbac into the organization account"""
    try:
        session = boto3.Session(profile_name=profile)
        sts_client = session.client("sts")
        response = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/{role_name}",
            RoleSessionName="AssumeRoleSession",
        )
        return response["Credentials"]
    except ClientError as e:
        raise OSError(f"Error assuming role: {e}") from e


def _get_child_accounts(aws_profile, credentials, organization_id):
    """get the chid accounts array"""
    session = boto3.Session(
        profile_name=aws_profile,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    org_client = session.client("organizations")
    paginator = org_client.get_paginator("list_accounts_for_parent")
    response_iterator = paginator.paginate(ParentId=organization_id)

    accounts = []
    for response in response_iterator:
        for account in response["Accounts"]:
            account_id = account["Id"]
            account_name = account["Name"]
            account_email = account["Email"]
            accounts.append((account_id, account_name, account_email))

    return accounts


def get_child_accounts(**kwargs):
    """return a dictionary of childe accounts for the organzation"""
    print("attemping to retrieve child accounts")
    aws_profile = kwargs.get("aws_profile", "default")
    print(kwargs)
    organization_account = kwargs.get("organization_account")
    organization_id = kwargs.get("organization_id")
    role_name = kwargs.get("automation_role", "core-automation-role")

    credentials = _assume_role(aws_profile, organization_account, role_name)
    child_account = _get_child_accounts(aws_profile, credentials, organization_id)
    return {
        "organization-account": organization_account,
        "organization-id": organization_id,
        "child-accounts": child_account,
    }


def add_show_parser(subparsers, cmd, description):
    """Add the show parser"""
    show_parser = subparsers.add_parser(
        cmd,
        description=description,
        usage="core organization show [<options>]",
        help=description,
    )
    show_parser.set_group_title(0, "Show actions")
    show_parser.set_group_title(1, "Available options")

    show_parser.add_argument(
        "-o",
        "--organization-account",
        required=True,
        help="Organization account number",
    )
    show_parser.add_argument(
        "-i", "--organization-id", required=True, help="Organization id"
    )
    show_parser.add_argument(
        "-r",
        "--automation-role",
        default="core-automation-role",
        help="Role name",
        required=False,
    )


def execute_show(**kwargs):
    """Show the organization accounts"""
    print("Show Organization Accounts")
    print(kwargs)


TASKS = {
    "show": ("Show organization accounts", execute_show, add_show_parser),
    "user": ("Manage user accounts", execute_user, add_user_parser),
}


def execute_organization(**kwargs):
    """Configure the client vars for the specified client."""
    task = kwargs.get("tasks")
    if task in TASKS:
        TASKS[task][1](**kwargs)
    else:
        print(f"Task {task} not found")


def get_organization_command(subparsers):
    """Get the parser for the configuration command"""

    DESCRPTION = "Manage the organization accounts"

    client = os.getenv("CLIENT", None)

    org_parser = subparsers.add_parser(
        "organization",
        description=DESCRPTION,
        usage="core organization [--client <name>]",
        help=DESCRPTION,
    )
    org_parser.set_group_title(0, "Configure actions")
    org_parser.set_group_title(1, "Available options")

    aws_profile = os.getenv("AWS_PROFILE", "default")

    subparsers = org_parser.add_subparsers(dest="tasks", help="sub-command help")

    any(v[2](subparsers, k, v[0]) for k, v in TASKS.items())

    org_parser.add_argument(
        "-c",
        "--client",
        required=client is None,
        help=f"Client alias name of the organization. Default: {client}",
        default=client,
    )
    org_parser.add_argument(
        "--aws-profile",
        required=False,
        help=f"AWS profile to use to access automation engine. default {aws_profile}",
        default=aws_profile,
    )
    org_parser.add_argument(
        "-s", "--show", help="Show the current configuration", action="store_true"
    )
    org_parser.add_argument(
        "-e", "--enable", help="Enable the service", action="store_true"
    )
    org_parser.add_argument(
        "-u", "--update", help="Update the service", action="store_true"
    )
    org_parser.add_argument(
        "-r",
        "--delete",
        help="Delete the configuration specified in --client",
        action="store_true",
    )

    return {"organization": (DESCRPTION, execute_organization)}
