from typing import Any
import os
import re
from rich.console import Console
from rich.prompt import Prompt

import zipfile

from core_helper.magic import MagicS3Client

import core_framework as util
from core_framework.models import TaskPayload
from core_framework.constants import V_PACKAGE_ZIP

import core_helper.aws as aws

from .exceptions import OrganizationNotSetException

console = Console()


def print_account_info(account_info):
    print("\nAccount Information\n")

    print(f"   Account Name: {account_info['Name']}")
    print(f"   Account ID  : {account_info['Id']}")
    print(f"   Account Email: {account_info['Email']}")


def cprint(msg: Any | None = None, **kwargs):
    """Print a message with color"""
    if msg is None:
        msg = ""
    console.print(msg, **kwargs)


def jprint(msg: Any | None = None):
    if msg is None:
        msg = ""
    console.print_json(msg)


def get_input(
    message: str, choices: list[str] | None = None, default: str | None = None
) -> str | None:
    """get input from the user.  Loop until they enter something"""
    while True:
        value = Prompt.ask(message, choices=choices, default=default)
        if not value:
            value = default
        if choices:
            if value:
                y = any(value.lower() == x.lower() for x in choices)
                if y:
                    return value
            console.print("Please select from the options.")
        else:
            return value


def get_organization_info():
    """get the organization information"""
    try:
        org_client = aws.org_client()
        response = org_client.describe_organization()
        id = response["Organization"]["Id"]
        master_account_id = response["Organization"]["MasterAccountId"]
        email = response["Organization"]["MasterAccountEmail"]
        response = org_client.describe_account(AccountId=master_account_id)
        name = response["Account"]["Name"]
        return {"Id": id, "AccountId": master_account_id, "Name": name, "Email": email}
    except org_client.exceptions.AWSOrganizationsNotInUseException:
        raise OrganizationNotSetException()


def get_account_info(account_id):
    try:
        org_client = aws.org_client()
        response = org_client.describe_account(AccountId=account_id)
        return response["Account"]
    except org_client.exceptions.AWSOrganizationsNotInUseException:
        raise OrganizationNotSetException()


def get_iam_user_name():
    try:
        iam_client = aws.iam_client()
        response = iam_client.get_user()
        return response["User"]["UserName"]
    except iam_client.exceptions.NoSuchEntityException:
        return "No user found"
    except Exception as e:
        print(f"Error retrieving IAM user name: {e}")
        return "Unknown user"


def check_admin_privileges(user_name):
    iam_client = aws.iam_client()
    paginator = iam_client.get_paginator("list_attached_user_policies")
    for page in paginator.paginate(UserName=user_name):
        for policy in page["AttachedPolicies"]:
            if policy["PolicyName"] == "AdministratorAccess":
                return True
    return False


def __gen_path(task_payload: TaskPayload) -> str:
    dd = task_payload.DeploymentDetails
    parts = [dd.Portfolio]
    if dd.App:
        parts.append(dd.App)
    if dd.BranchShortName:
        parts.append(dd.BranchShortName)
    parts.append(re.sub(r"[^a-zA-Z0-9]", "", dd.Build or ""))
    return "-".join(parts)


def package_project(root_dir: str, task_payload: TaskPayload) -> str:

    # if the basedir of root_dir is not 'platform' then fail
    if not root_dir.endswith("platform"):
        raise ValueError(
            "Invalid root directory. You must specify a platform directory"
        )

    # use the python zipfile module to create a zip file of the project and include only the subfoloders "vars", "components"
    # and output the zip to the file "package.zip" in the "temp" directory

    path = __gen_path(task_payload)

    temp_dir = util.get_temp_dir(path)
    fn = os.path.join(temp_dir, V_PACKAGE_ZIP)

    with zipfile.ZipFile(fn, "w") as zipf:
        for root, _, files in os.walk(root_dir):
            for file in files:
                zipf.write(os.path.join(root, file))
    return temp_dir


def upload_project(task_payload: TaskPayload, temp_dir: str) -> str:
    # upload the zip file to the s3 bucket

    file_key = task_payload.Package.Key
    bucket_name = task_payload.Package.BucketName
    region = task_payload.Package.BucketRegion

    # Give me an actual s3 resource or my virtual 'file' bucket resource.  Depends on util.is_use_s3()
    bucket = MagicS3Client.get_bucket(region, bucket_name)

    fn = os.path.join(temp_dir, V_PACKAGE_ZIP)

    with open(fn, "rb") as data:
        bucket.put_object(Key=file_key, Body=data)

    return file_key
