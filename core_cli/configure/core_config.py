""" Manage the ~/core/config configuration file """

from datetime import datetime
import os
import sys
import configparser
import json
from typing import Optional
import boto3
from botocore.exceptions import ClientError

import core_helper.aws as aws

from .client_vars import get_region_role

aws_credentials = None


def assume_automation_role(**kwargs) -> Optional[dict]:
    """assume the core automation role, if there is no role because you haven't even created it, then we try to assume 'Developer' role"""
    global aws_credentials

    if aws_credentials:
        return aws_credentials

    try:
        role_name = kwargs.get("automation_role", None)
        # The organization information should be in the billing_account.  If not, let's assume we are logged in tot he billing account and that would man
        # client_account has the right account number information.
        account_number = kwargs.get(
            "billing_account", kwargs.get("client_account", None)
        )

        if not account_number:
            raise ValueError(
                "One of 'billing_account' or 'client_account' must be provided."
            )

        if role_name:
            role_arn = f"arn:aws:iam::{account_number}:role/{role_name}"
            print(f"Attempting to assume '{role_name}' role: {role_arn}")
            aws_credentials = aws.assume_role(role=role_arn)
            if aws_credentials:
                return aws_credentials

        # Didn't work with the configured role, so, let's try "Developer" role
        role_arn = f"arn:aws:iam::{account_number}:role/RBAC_Developer"
        print(f"Attempting to assume 'RBAC_Developer' role: {role_arn}")

        aws_credentials = aws.assume_role(role=role_arn)

    except ClientError as e:
        if "AccessDenied" in str(e):
            print(
                f"You do not have the correct permissions to assume the automation role [{role_name}].  We will continue ..."
            )
        else:
            raise OSError(f"Error assuming role {e}") from e

    return aws_credentials


def get_configuration_file():
    """Return the path to the configuration file."""
    config_folder = os.path.expanduser("~/.config")
    if not os.path.exists(config_folder):
        os.makedirs(config_folder, exist_ok=True)
    config_folder = os.path.join(config_folder, "core")
    if not os.path.exists(config_folder):
        os.makedirs(config_folder, exist_ok=True)
    config_file = os.path.join(config_folder, "config")
    return config_file


def _get_core_configurator() -> configparser.ConfigParser:
    """Read the core configuration configuration parser filled with."""
    config = configparser.ConfigParser()

    try:
        config_file = get_configuration_file()
        config.read(config_file)

    except PermissionError:
        print(
            "WARNING: Permission denied when trying to create or read the configuration file."
        )
    except configparser.Error as e:
        print(f"WARNING: Error reading configuration file: {e}")
    except FileNotFoundError as e:
        print(f"WARNING: File not found error: {e}")

    return config


def get_core_config_data(client: str) -> dict:
    """
    Read the configuration for the specified client, and if the client
    isn't found, create a new configuration file for the client.

    Args:
        client (str): the alias name for the organization
    """

    config = _get_core_configurator()
    if config.has_section(client):
        return dict(config.items(client))
    return {}


def set_config_value(config, client, prompt, key, default_value):
    """Read the user input from the console and set the configuration value."""
    if config.has_option(client, key):
        previous_value = config.get(client, key)
    else:
        previous_value = default_value
    new_value = input(prompt.format(previous_value))
    if not new_value:
        new_value = previous_value
    if new_value == "-":
        new_value = ""
    config.set(client, key, new_value)


def get_organizations_information(**kwargs):
    """return organization information for the AWS Profile"""
    organization_id = ""
    account_id = ""
    account_name = ""
    try:
        region, role = get_region_role(**kwargs)
        client = aws.org_client(region=region, role=role)
        orginfo = client.describe_organization()
        if "Organization" in orginfo:
            organization_id = orginfo["Organization"]["Id"]
            account_id = orginfo["Organization"]["MasterAccountId"]
            response = client.describe_account(AccountId=account_id)
            if "Account" in response:
                account_name = response["Account"]["Name"]
    except Exception:  # pylint: disable=broad-except
        pass

    return organization_id, account_id, account_name


def get_ou_id_by_name(ou_name, organizational_units):
    """Return the OU Id from its name in the list of OU's provided.  Case inensiive search."""
    for ou in organizational_units:
        if ou["Name"].lower() == ou_name.lower():
            return ou["Id"]
    return None


def list_accounts_for_ou(ou_id):
    """Return all the accounts under the specific OU"""
    try:
        # Create an Organizations client
        org_client = boto3.client("organizations")

        # Initialize pagination
        paginator = org_client.get_paginator("list_accounts_for_parent")

        # Iterate through paginated results
        accounts = []
        for page in paginator.paginate(ParentId=ou_id):
            accounts.extend(page["Accounts"])

        return accounts
    except ClientError as e:
        print(f"Error occurred: {e}")
        return []


def list_organizational_units(root_id, **kwargs):
    """Get the organization units UNDER the root_id specified.  Can use in a hierarchy"""
    try:
        # Create an Organizations client
        region, role = get_region_role(**kwargs)
        client = aws.org_client(region=region, role=role)

        # Initialize pagination
        paginator = client.get_paginator("list_organizational_units_for_parent")

        # Iterate through paginated results
        organizational_units = []
        for page in paginator.paginate(ParentId=root_id):
            organizational_units.extend(page["OrganizationalUnits"])

        return organizational_units
    except ClientError as e:
        if "InvalidInputException" in str(e) or "AccessDenied" in str(e):
            print(
                "You do not have the correct permissions to list organizational units.  We will continue ..."
            )
            return []
        raise OSError(f"Error occurred: {e}") from e


def list_organization_accounts(**kwargs):
    """List all accounts in the organization"""
    try:
        # Create an Organizations client
        region, role = get_region_role(**kwargs)
        client = aws.org_client(region=region, role=role)

        # Initialize pagination
        paginator = client.get_paginator("list_accounts")

        # Iterate through paginated results
        accounts = []
        for page in paginator.paginate():
            accounts.extend(page["Accounts"])

        return accounts
    except ClientError as e:
        print(f"Error occurred: {e}")
        return None


def list_roles_with_keywords(substrings, **kwargs):
    """get a list of roles with the keywords in their name"""
    try:
        # Create an IAM client
        region, role = get_region_role(**kwargs)
        client = aws.iam_client(region=region, role=role)

        # Initialize pagination
        paginator = client.get_paginator("list_roles")

        # Iterate through paginated results
        matching_roles = []
        for page in paginator.paginate():
            for role in page["Roles"]:
                role_name = role["RoleName"]
                if any(
                    substring.lower() in role_name.lower() for substring in substrings
                ):
                    matching_roles.append(role_name)

        return matching_roles
    except ClientError as e:
        print(f"Error occurred: {e}")
        return None


class DateTimeEncoder(json.JSONEncoder):
    """handle ISO data/time fields in JSON objects"""

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def update_core_config(**kwargs):
    """Make changes to and update the core configuration file."""

    aws_profile = kwargs.get("aws_profile")

    print(f"Core Automation Configuration\n" f"AWS Profile: {aws_profile}\n")

    client = kwargs.get("client")

    config = _get_core_configurator()

    if kwargs.get("show"):
        config.write(sys.stdout)
        return

    if not config.has_section(client):
        config.add_section(client)

    default_account = kwargs.get("client_account")

    organization_id, organization_account, organization_name = (
        get_organizations_information()
    )
    if organization_id:

        print("HINT:")
        print(
            f"Organization: {organization_id}  Account: {organization_account}  Name: {organization_name or '<unknown>'}"
        )
        print("Current CORE Organization Acocunts:")

        organizational_units = list_organizational_units(organization_id, **kwargs)
        if organizational_units:
            ou_id = get_ou_id_by_name("core", organizational_units)
            accounts = list_accounts_for_ou(ou_id, **kwargs)
            for account in accounts:
                print(f"  Account ID: {account['Id']}  Name: ({account['Name']})")
    else:
        print("We tried to find Hints.  But you have no permissions")

    keywords = ["Core", "Automation", "Developer"]

    # Retrieve the list of matching roles
    matching_roles = list_roles_with_keywords(keywords, **kwargs)

    # Print the list of matching roles or a message if none are found
    if matching_roles:
        print("\nHere are some roles you might consider as the automation role:")
        for role in matching_roles:
            print(f"  - {role}")

    region_default = "ap-southeast-1"

    print(
        f"\nEnter configuration values for client: {client}\n"
        f"Enter a dash (-) to remove the value"
    )

    prompts_keys = [
        (
            "Default client region (where your landing zones are)       [{}]: ",
            "client_region",
            region_default,
        ),
        (
            "Automation (Build) account                                 [{}]: ",
            "automation_account",
            default_account,
        ),
        (
            "Automation (Build) region of the engine and CMDB database  [{}]: ",
            "master_region",
            region_default,
        ),
        (
            "Automation (Build) region of the FACTS/Artefacts S3 bucket [{}]: ",
            "bucket_region",
            region_default,
        ),
        (
            "Automation Role name                                       [{}]: ",
            "automation_role",
            "AutomationRole",
        ),
        (
            "Organization/Billing/Control Tower/SSO account             [{}]: ",
            "organization_account",
            organization_account,
        ),
        (
            "Organization id                                            [{}]: ",
            "organization_id",
            organization_id,
        ),
        (
            "IAM Account                                                [{}]: ",
            "iam_account",
            default_account,
        ),
        (
            "Audit/Log/Cloudwatch/KMS/Secrets Account                   [{}]: ",
            "audit_account",
            default_account,
        ),
        (
            "Security Hub/Guard Duty/SEIM Account                       [{}]: ",
            "security_account",
            default_account,
        ),
        (
            "Scope prefix (different DB in the same automation account) [{}]: ",
            "scope_prefix",
            "",
        ),
    ]

    for prompt, key, default_value in prompts_keys:
        set_config_value(config, client, prompt, key, default_value)

    print("OK, we are done.\n\nHere is the configuration we have for you:\n")

    config_file = get_configuration_file()

    # Write the updated configuration back to the file
    with open(config_file, "w", encoding="utf8") as configfile:
        config.write(configfile)

    config.write(sys.stdout)
