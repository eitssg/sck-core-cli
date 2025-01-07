from ..cmdparser import ExecuteCommandsType


def execute_info(args):
    pass


def add_info_parser(subparsers) -> ExecuteCommandsType:
    """Add the info parser to the subparsers"""

    description = "Information about the engine"

    subparsers.add_parser(
        "info",
        description=description,
        usage="core engine info",
        help="Show information about the engine",
    )

    return {"info": (description, execute_info)}
