from rich.table import Table
from rich import box

from ..cmdparser import ExecuteCommandsType
from core_cli import __version__

from ..environment import get_environment
from ..console import cprint


def execute_info(**kwargs):

    cprint(f"Engine Information v{__version__}\n")

    cprint("This is the engine information\n")

    # print all environment variables ins a table
    table = Table(box.SQUARE)
    table.add_column("Environment Variable")
    table.add_column("Value")

    envs = get_environment()
    for key, value in envs.items():
        table.add_row(key, value)

    cprint(table)


def add_info_parser(subparsers) -> ExecuteCommandsType:
    """Add the info parser to the subparsers"""

    description = "Information about the engine"

    subparsers.add_parser(
        "info",
        description=description,
        help="Show information about the engine",
    )

    return {"info": (description, execute_info)}
