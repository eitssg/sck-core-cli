"""mange role policy"""

import boto3
import json

from ..cmdparser import ExecuteCommandsType


def ensure_user_can_assume_role(client_account, role_name, user_arn):  # noqa E501
    # Initialize the boto3 client for IAM
    iam_client = boto3.client("iam")

    # Get the current trust policy of the role
    try:
        response = iam_client.get_role(RoleName=role_name)
        trust_policy = response["Role"]["AssumeRolePolicyDocument"]
    except iam_client.exceptions.NoSuchEntityException:
        print(f"Role {role_name} does not exist in account {client_account}")
        return

    # Check if the user is already in the trust policy
    for statement in trust_policy["Statement"]:
        if statement["Effect"] == "Allow" and "AWS" in statement["Principal"]:
            if isinstance(statement["Principal"]["AWS"], list):
                if user_arn in statement["Principal"]["AWS"]:
                    print(f"{user_arn} already has permission to assume {role_name}")
                    return
            else:
                if statement["Principal"]["AWS"] == user_arn:
                    print(f"{user_arn} already has permission to assume {role_name}")
                    return

    # Modify the trust policy to add the user
    for statement in trust_policy["Statement"]:
        if statement["Effect"] == "Allow" and "Service" in statement["Principal"]:
            if "sts.amazonaws.com" in statement["Principal"]["Service"]:
                if "AWS" in statement["Principal"]:
                    if isinstance(statement["Principal"]["AWS"], list):
                        statement["Principal"]["AWS"].append(user_arn)
                    else:
                        statement["Principal"]["AWS"] = [
                            statement["Principal"]["AWS"],
                            user_arn,
                        ]
                else:
                    statement["Principal"]["AWS"] = user_arn
                break
    else:
        # If no matching statement is found, add a new statement
        new_statement = {
            "Effect": "Allow",
            "Principal": {"AWS": user_arn},
            "Action": "sts:AssumeRole",
        }
        trust_policy["Statement"].append(new_statement)

    # Update the trust policy of the role
    iam_client.update_assume_role_policy(
        RoleName=role_name, PolicyDocument=json.dumps(trust_policy)
    )

    print(f"{user_arn} has been granted permission to assume {role_name}")


def add_user(**kwargs):
    """add user information to role"""
    print(kwargs)

    print("Add User to Automation Role:\n")
    client = kwargs.get("client")
    aws_profile = kwargs.get("aws_profile")
    automation_role = kwargs.get("automation_role")
    client_account = kwargs.get("client_account")
    client_region = kwargs.get("client_region")
    user_arn = kwargs.get("user_arn")

    print("Client         : ", client)
    print("AWS Profile    : ", aws_profile)
    print("Client Account : ", client_account)
    print("Client Region  : ", client_region)
    print("Automation Role: ", automation_role)
    print("User ARN       : ", user_arn)

    # Example usage
    ensure_user_can_assume_role(
        client_account=client_account, role_name=automation_role, user_arn=user_arn
    )


def remove_user(**kwargs):
    """remove user"""
    print("Remove User")
    print(kwargs)


def list_user(**kwargs):
    """list user"""
    print("List User")
    print(kwargs)


CHOICES: ExecuteCommandsType = {
    "add": ("Add User", add_user),
    "remove": ("Remove User", remove_user),
    "list": ("List User", list_user),
}


def get_user_tasks(parser) -> ExecuteCommandsType:
    """add the user parser"""

    description = "Manage user accounts"

    subparser = parser.add_parser(
        "user",
        description=description,
        choices=CHOICES,
        usage="core organization user [<unit>] [<options>]",
        help=description,
    )
    subparser.set_group_title(0, "User tasks")
    subparser.set_group_title(1, "Available options")

    subparser.add_argument("unit", choices=CHOICES.keys(), help="Task to perform")

    subparser.add_argument(
        "-p", "--profile", default="default", help="AWS profile", required=False
    )
    subparser.add_argument(
        "-a",
        "--account",
        default=None,
        help="Organization account number",
        required=True,
    )
    subparser.add_argument(
        "-r", "--role", default="core-automation-role", help="Role name", required=False
    )

    return {"user": (description, execute_user)}


def execute_user(**kwargs):
    """run the suer command"""
    unit = kwargs.get("unit")
    if unit in CHOICES:
        CHOICES[unit][1](**kwargs)
    else:
        raise ValueError(f"Task {unit} not found")
