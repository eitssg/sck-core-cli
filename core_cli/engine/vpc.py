from ..cmdparser import ExecuteCommandsType


def add_vpc_parser(subparsers) -> ExecuteCommandsType:
    """add the clean parser"""

    description = "Manage default VPC's in all zones listed in the account registry"

    subparser = subparsers.add_parser(
        "vpc",
        usage="core engine vpc [<options>]",
        description=description,
        help=description,
    )
    subparser.set_group_title(0, "VPC tasks")
    subparser.set_group_title(1, "Available options")

    return {"vpc": (description, execute_vpc)}


def execute_vpc(**kwargs):
    """execute the command"""
    print("VPC")
