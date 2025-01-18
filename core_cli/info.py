from rich.table import Table
from rich import box

from .common import cprint

from .cmdparser import ExecuteCommandsType

from ._version import __version__

from .environment import print_environmnt


def execute_info(**kwargs):

    cprint(f"Core Automation Information v{__version__}\n")

    cprint("This is the core CLI information:\n")

    print_environmnt()


def get_info_command(subparsers) -> ExecuteCommandsType:

    DESCRIPTION = "Display information about the core subsystem"

    config_parser = subparsers.add_parser(
        "info", description=DESCRIPTION, usage="core info", help=DESCRIPTION
    )
    config_parser.set_group_title(0, "Configure actions")
    config_parser.set_group_title(1, "Available options")

    return {"info": (DESCRIPTION, execute_info)}
