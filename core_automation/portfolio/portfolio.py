import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

client_session = None
client_credentials = None


def assume_core_role(**kwargs) -> dict:
    """Assume the core role"""
    global client_credentials

    if client_credentials:
        return client_credentials

    try:
        role_name = kwargs.get("role_name", None)
        account_number = kwargs.get("master_acccount", None)

        if not role_name or not account_number:
            raise ValueError("Both 'role_name' and'master_acccount' must be provided.")

        role_arn = f"arn:aws:iam::{account_number}:role/{role_name}"

        session = boto3.Session()
        sts_client = session.client("sts")
        response = sts_client.assume_role(RoleArn=role_arn, DurationSeconds=3600)
        if (
            response["ResponseMetadata"]["HTTPStatusCode"] != 200
            or "Credentials" not in response
        ):
            raise OSError("Error assuming role")

        client_credentials = response["Credentials"]
        return client_credentials
    except ClientError as e:
        raise OSError("Error assuming role") from e


def list_portfolios(**kwargs):
    """list portfolios"""
    print(kwargs)
    credentials = assume_core_role(**kwargs)
    dynamodb = boto3.client(
        "dynamodb",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    print("List Portfolios")

    table = dynamodb.Table("ccoe_registry_portfolios")

    response = table.query(
        KeyConditionExpression=Key("pk").eq("id#1") & Key("sk").begins_with("cart#"),
        FilterExpression=Attr("name").eq("SomeName"),
    )


def add_portfolio(**kwargs):
    """add portfolio"""
    print(kwargs)
    print("Add Portfolio")


def update_portfolio(**kwargs):
    """add/update portfolio"""
    print(kwargs)
    print("Add/Update Portfolio")


def delete_portfolio(**kwargs):
    """delete portfolio"""
    print(kwargs)
    print("Delete Portfolio")


TASKS = {
    "list": ("List all portfolios", list_portfolios),
    "add": ("Add new portfolio", add_portfolio),
    "update": ("Update portfolio", update_portfolio),
    "delete": ("Delete portfolio", delete_portfolio),
}


def execute_portfolio(**kwargs):
    """Execute the portfolio command"""
    action = kwargs.get("action", None)
    if action in TASKS:
        TASKS[action][1](**kwargs)


def get_portfolio_command(subparsers):
    """add the portfolio parser"""

    description = "Manage portfolios"

    subparser = subparsers.add_parser(
        "portfolio",
        description=description,
        usage="core engine portfolio [<action>] [<args>]",
        choices=TASKS,
        help=description,
    )

    subparser.set_group_title(0, "Avalable actions")
    subparser.set_group_title(1, "Available options")

    subparser.add_argument("action", choices=TASKS.keys(), help="The action to perform")

    subparser.add_argument("-p", "--portfolio", help="Specifiy one portfolio by name")
    subparser.add_argument(
        "-b", "--branch", help="Specify the portfolio zone/environment branch"
    )

    return {"portfolio": (description, execute_portfolio)}
