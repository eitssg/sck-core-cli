from .._version import __version__


def get_epilog():
    """return the epilog"""
    return """

Copyright (c) 2024. EI

"""


def add_source_parser(subparsers):
    """add the source parser"""

    description = "Manage automatin engine source clode"

    prolog = f"Core Automatoin Engine version {__version__}\n{description}"

    subparser = subparsers.add_parser(
        "source",
        usage="core engine source [<action>] [<args>]",
        description=prolog,
        epilog=get_epilog(),
        help=description,
    )
    subparser.set_group_title(0, "Avalable actions")
    subparser.set_group_title(1, "Avalable options")

    subparser.add_argument(
        "action",
        nargs="*",
        choices=["pull"],
        help="Search CloudTrail for core-automation GitPull",
    )

    return {"source": (description, execute_source)}


def execute_source(**kwargs):
    """execute the command"""
    print("Source")
