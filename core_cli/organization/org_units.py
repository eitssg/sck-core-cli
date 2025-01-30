import core_framework as util

import core_helper.aws as aws

from core_cli import __version__
from ..console import (
    get_iam_user_name,
    get_organization_info,
    get_account_info,
    check_admin_privileges,
)

from ..cmdparser import ExecuteCommandsType


def get_root_id():
    """Get the root ID of the organization."""
    org_client = aws.org_client()
    response = org_client.list_roots()
    roots = response["Roots"]
    root_id = roots[0]["Id"]
    return root_id


def get_ou_info(ou_id):
    """Get the organizational unit information."""
    org_client = aws.org_client()
    response = org_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
    return response["OrganizationalUnit"]


def list_organizational_units(parent_id):
    """List all organizational units for a given parent ID."""

    org_client = aws.org_client()
    paginator = org_client.get_paginator("list_organizational_units_for_parent")
    response_iterator = paginator.paginate(ParentId=parent_id)

    ous = []
    for response in response_iterator:
        ous.extend(response["OrganizationalUnits"])

    return ous


def get_child_accounts(parent_id):
    """Get the child accounts array"""

    org_client = aws.org_client()
    paginator = org_client.get_paginator("list_accounts_for_parent")
    response_iterator = paginator.paginate(ParentId=parent_id)

    accounts = []
    for response in response_iterator:
        for account in response["Accounts"]:
            account_id = account["Id"]
            account_name = account["Name"]
            account_email = account["Email"]
            accounts.append((account_id, account_name, account_email))

    return accounts


def print_organizational_units_tree(parent_id: str, level: int = 0):
    """Print the organizational units and accounts tree structure incrementally."""
    indent = "|   " * level
    if level == 0:
        print(f"|-- Root (ID: {parent_id})")
    else:
        ou_info = get_ou_info(parent_id)
        print(f"{indent}|-- {ou_info['Name']} (ID: {ou_info['Id']})")

    accounts = get_child_accounts(parent_id)
    for account in accounts:
        print(
            f"{indent}|   |-- Account: {account[1]} (ID: {account[0]}, Email: {account[2]})"
        )

    ous = list_organizational_units(parent_id)
    for ou in ous:
        print_organizational_units_tree(ou["Id"], level + 1)


TASKS: ExecuteCommandsType = {}


def get_org_unit_tasks(subparsers) -> ExecuteCommandsType:
    """Get the org unit tasks"""

    description = "Manage the organization units"
    org_unit_parser = subparsers.add_parser(
        "ou",
        description=description,
        usage="core organization org_units [<task>] [<args>]",
        help=description,
    )
    org_unit_parser.set_group_title(0, "Org unit tasks")
    org_unit_parser.set_group_title(1, "Available options")

    task_parsers = org_unit_parser.add_custom_subparsers(dest="task", metavar="<task>")
    TASKS.update(get_ou_list_task(task_parsers))

    return {
        "ou": (description, execute_org_units),
    }


def execute_org_units(**kwargs):
    """Execute the org unit tasks"""
    task = kwargs.get("task")
    if task in TASKS:
        TASKS[task][1](**kwargs)
    else:
        print(f"Task {task} not found")


def get_ou_list_task(subparsers) -> ExecuteCommandsType:
    """Add the list parser"""

    description = "List the organization units"
    list_parser = subparsers.add_parser(
        "list",
        description=description,
        usage="core organization org_units list [<options>]",
        help=description,
    )
    list_parser.set_group_title(0, "List actions")
    list_parser.set_group_title(1, "Available options")

    return {"list": (description, execute_list)}


def execute_list(**kwargs):
    """List the organization units"""

    print(f"Core Automation Organizations v{__version__}\n")

    user_name = get_iam_user_name()

    print(f"Welcome {user_name}!\n")

    aws_profile = util.get_aws_profile()

    print(f'You will be using AWS Profile: "{aws_profile}"\n')

    org_info = get_organization_info()

    print("Organization Information\n")

    organization_id = org_info["Id"]
    root_id = get_root_id()

    print(f"   Organization Name: {org_info['Name']}")
    print(f"   Organization ID  : {organization_id}")
    print(f"   Master Account   : {org_info['AccountId']}")
    print(f"   Master Email     : {org_info['Email']}")

    aws_account_id = kwargs["user"]["account"]
    account_info = get_account_info(aws_account_id)

    print("\nAccount Information\n")

    print(f"   Account Name: {account_info['Name']}")
    print(f"   Account ID  : {account_info['Id']}")
    print(f"   Account Email: {account_info['Email']}")

    if org_info["AccountId"] != account_info["Id"]:
        print(
            f"\nYou are not in the master account. You are in account {account_info['Name']}."
        )
        print("Please run this command from the master account.\n")
        print("Aborted")
        return

    is_admin = check_admin_privileges(user_name)

    if not is_admin:
        print("\nYou do not have administrator privileges in this account.")
        print("Please run this command from an account with administrator privileges.")
        print("Perhaps choose a different AWS_PROFILE.\n")
        print("Aborted")
        return

    print(
        "\nCongratulations! We have checked and you are an admin!\nYou may continue with the query.\n"
    )

    print("Organizational Units Tree:\n")

    print_organizational_units_tree(root_id)

    print("")
    print("Done")
