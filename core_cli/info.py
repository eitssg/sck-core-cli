import json

from .cmdparser import ExecuteCommandsType

from ._version import __version__


def execute_info(**kwargs):
    print(f"Version {__version__}\n\n")

    print(json.dumps(kwargs, indent=4))


def get_info_command(subparsers) -> ExecuteCommandsType:

    DESCRIPTION = "Display information about the core subsystem"

    config_parser = subparsers.add_parser(
        "info", description=DESCRIPTION, usage="core info", help=DESCRIPTION
    )
    config_parser.set_group_title(0, "Configure actions")
    config_parser.set_group_title(1, "Available options")

    return {"info": (DESCRIPTION, execute_info)}
