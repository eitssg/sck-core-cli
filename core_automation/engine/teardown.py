def add_teardown_parser(subparsers) -> dict:
    """add the source parser"""

    description = (
        "Remove Core Automation CloudFormation Stacks, Databases, and S3 Buckets"
    )

    subparser = subparsers.add_parser(
        "teardown",
        usage="core engine teardown [<options>]",
        description=description,
        help=description,
    )
    subparser.set_group_title(0, "Teardown tasks")
    subparser.set_group_title(1, "Available options")

    return {"teardown": (description, execute_teardown)}


def execute_teardown(**kwargs):
    """execute the command"""
    print("Teardown")
