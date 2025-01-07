""" THe Deploy module is responsible for deploying the Core Automation subsystem """

import os

from ...cmdparser import ExecuteCommandsType


def get_epilog():
    """return the epilog"""
    return """Options can also be set via environment variables:
    UNITS
    CLIENT, SCOPE
    BRANCH, BUILD
"""


def unit_all(**kwargs):
    """a unit to deploy"""
    print(kwargs.get("unit"))


def unit_invoker(**kwargs):
    """a unit to deploy"""
    print(kwargs.get("unit"))


def unit_runner(**kwargs):
    """a unit to deploy"""
    print(kwargs.get("unit"))


def unit_compiler(**kwargs):
    """a unit to deploy"""
    print(kwargs.get("unit"))


def unit_lambda(**kwargs):
    """a unit to deploy"""
    print(kwargs.get("unit"))


def unit_legacy(**kwargs):
    """a unit to deploy"""
    print(kwargs.get("unit"))


def unit_apidb(**kwargs):
    """a unit to deploy"""
    print(kwargs.get("unit"))


def unit_codecommit(**kwargs):
    """a unit to deploy"""
    print(kwargs.get("unit"))


def unit_facts(**kwargs):
    """a unit to deploy"""
    print(kwargs.get("unit"))


def get_default_units(aslist: bool = False):
    """return the default units"""
    units = os.getenv("UNITS", "invoker runner compiler facts")
    if len(units) > 0:
        return units.split(" ") if aslist else units
    return units


UNITS: ExecuteCommandsType = {
    "all": ("Everything", unit_all),
    "invoker": ("Invoker Lambdas", unit_invoker),
    "runner": ("Runner Lambdas", unit_runner),
    "compiler": ("Component anddeployspe compiler Lambdas", unit_compiler),
    "api-legacy": ("Legacy API Lambdas and DynamoDB tables", unit_legacy),
    "api-lambda": ("API Lambda", unit_lambda),
    "api-db": ("API DynamoDB tables", unit_apidb),
    "codecommit": ("CodeCommit Lambdas", unit_codecommit),
    "facts": ("Facts in S3", unit_facts),
}


def add_deploy_parser(subparsers) -> ExecuteCommandsType:
    """Create parser for the command line for the deploy command"""

    description = "Manage and deploy the Core Automation subsystem"

    client = os.environ.get("CLIENT", None)

    parser = subparsers.add_parser(
        "deploy",
        description=description,
        usage="core engine deploy [<untis>] [<options>]",
        choices=UNITS,
        epilog=get_epilog(),
        help=description,
    )

    aws_profile = os.getenv("AWS_PROFILE", client)

    parser.set_group_title(0, "Avaiable units")
    parser.set_group_title(1, "Available options")

    parser.add_argument("units", nargs="+", choices=UNITS.keys())

    parser.add_argument(
        "-c",
        "--client",
        help=f"Client alias name of the organization: Default: {client}",
        required=client is None,
        default=client,
    )
    parser.add_argument(
        "-s",
        "--scope",
        help="Deployment scope or namespacing deployments",
        required=False,
    )
    parser.add_argument("-b", "--branch", help="Branch name", required=False)
    parser.add_argument("-n", "--build", help="Build name", required=False)
    parser.add_argument(
        "--api-branch",
        help="Use a specific branch of the API",
        required=False,
        default="master",
    )
    parser.add_argument(
        "--aws-profile", help="AWS profile name", required=False, default=aws_profile
    )

    # get a list of units except for all and default
    keys = [key for key in UNITS if key not in ["all", "default"]]
    parser.add_argument(
        "--skip",
        nargs="*",
        choices=keys,
        help=f"Specify the <units> (one or more) to skip when running operation.\nChoices: {', '.join(keys)}",
    )

    return {"deploy": (description, execute_deploy)}


def execute_deploy(**kwargs):
    """Deploy the services"""
    units = kwargs.get("units", [])
    if not units:
        units = get_default_units(True)
    for u in units:
        if u in UNITS:
            UNITS[u][1](**kwargs)
        else:
            print("Unknown Unit")
