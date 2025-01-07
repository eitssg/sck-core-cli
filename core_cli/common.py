import core_helper.aws as aws

from .exceptions import OrganizationNotSetException


def get_input(message: str, options: list[str], default: str | None = None) -> str:
    """get input from the user"""
    options_str = "/".join(options)
    message = f"{message} [{options_str}]: "
    while True:
        value = input(message)
        if not value and default:
            return default
        y = any(value.lower() == x.lower() for x in options)
        if y:
            return value
        print("Please select from the options.")


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
