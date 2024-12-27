from ._version import __version__


def execute_info(**kwargs):
    print(f"Version {__version__}")


def get_info_command(subparsers):

    DESCRIPTION = "Display information about the core subsystem"

    config_parser = subparsers.add_parser(
        "info", description=DESCRIPTION, usage="core info", help=DESCRIPTION
    )
    config_parser.set_group_title(0, "Configure actions")
    config_parser.set_group_title(1, "Available options")

    return {"info": (DESCRIPTION, execute_info)}
