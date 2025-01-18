""" Delete S3 bucket contents for core-automation """

import os
import re

import boto3
from botocore.exceptions import ClientError

from ..cmdparser import ExecuteCommandsType


def assume_role(profile, account_id, role_name):
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


def add_clean_parser(subparsers) -> ExecuteCommandsType:
    """add the clean parser"""

    description = "Delete S3 files for a given branch of an app"

    subparser = subparsers.add_parser(
        "clean",
        description=description,
        help=description,
    )
    subparser.set_group_title(0, "Clean tasks")
    subparser.set_group_title(1, "Available options")

    portfolio = os.environ.get("PORTFOLIO", None)
    app = os.environ.get("APP", None)
    branch = os.environ.get("BRANCH", None)
    bucket_region = os.environ.get(
        "BUCKET_REGION", os.environ.get("AWS_REGION", "ap-southeast-1")
    )
    bucket_name = os.environ.get("BUCKET_NAME", None)

    subparser.add_argument(
        "-p",
        "--portfolio",
        default=portfolio,
        help="Portfolio name",
        required={not portfolio},
    )
    subparser.add_argument(
        "-a", "--app", default=app, help="Application name", required={not app}
    )
    subparser.add_argument(
        "-b", "--branch", default=branch, help="Branch name", required={not branch}
    )
    subparser.add_argument(
        "--bucket-region",
        default=bucket_region,
        help="S3 Bucket Region",
        required=False,
    )
    subparser.add_argument(
        "--bucket-name", default=bucket_name, help="S3 Bucket Name", required=False
    )

    return {"clean": (description, execute_clean)}


def make_defaults(**kwargs):
    """make the defaults"""
    client = kwargs.get("client", None)
    bucket_region = kwargs.get(
        "bucket_region", os.environ.get("AWS_REGION", "ap-southeast-1")
    )
    if kwargs.get("bucket_name", None) is None:
        kwargs["bucket_name"] = f"{client}-core-automation-{bucket_region}"
    return kwargs


def execute_clean(**kwargs):
    """execute the command"""
    kwargs = make_defaults(**kwargs)

    client = kwargs.get("client")
    portfolio = kwargs.get("portfolio")
    app = kwargs.get("app")
    branch = kwargs.get("branch")
    master_account = kwargs.get("master_account")
    bucket_name = kwargs.get("bucket_name")
    bucket_region = kwargs.get("bucket_region")
    aws_profile = kwargs.get("aws_profile")
    automation_role = kwargs.get("automation_role")

    if not portfolio or not app or not branch or not bucket_name:
        raise ValueError("Portfolio, App, Branch and Bucket Name are required.")

    branch_short_name = re.sub(r"[^a-z0-9\\-]", "-", branch.lower())[0:20].rstrip("-")
    common_key_path = f"{portfolio}/{app}/{branch_short_name}"

    print("Clear Contents of S3 Bucket\n")

    print(f"Client         : {client}")
    print(f"Master Account : {master_account}")
    print(f"Automation Role: {automation_role}")
    print(f"AWS Profile    : {aws_profile}")
    print(f"Bucket Name    : {bucket_name}")
    print(f"Region         : {bucket_region}")
    print(f"Folder         : {common_key_path}")

    print("\nOne moment...")

    delete_keys = [
        {"Key": f"/packages/{common_key_path}"},
        {"Key": f"/artefacts/{common_key_path}"},
        {"Key": f"/files/build/{common_key_path}"},
    ]

    try:
        credentials = assume_role(aws_profile, master_account, automation_role)
        session_token = credentials["SessionToken"]
        session = boto3.Session(
            profile_name=aws_profile,
            region_name=bucket_region,
            aws_session_token=session_token,
        )
        s3 = session.client("s3")
        response = s3.delete_objects(
            Bucket=bucket_name, Delete={"Objects": delete_keys, "Quiet": False}
        )
    except ClientError as e:
        raise OSError(f"{e}") from e

    items = response["Deleted"]
    print("\nDeleted Items:")
    for item in items:
        print(f"  - {item['Key']}")
    print("\nDone.")

    print(kwargs)
