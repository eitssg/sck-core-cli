"""Configuration Module Package"""

from .core_config import update_core_config

from core_framework.constants import (
    P_PORTFOLIO,
    P_APP,
    P_BRANCH,
    P_BUILD,
)


def get_configure_command(subparsers):
    """Get the parser for the configuration command"""

    description = "Configure the core subsystem client vars"

    cp = subparsers.add_parser(
        "configure",
        description=description,
        help=description,
    )
    cp.set_group_title(0, "Configure actions")
    cp.set_group_title(1, "Available options")

    cp.add_argument(
        "task", dest="task", metavar="<task>", help="Task name", required=False
    )

    cp.add_argument(
        "-p",
        "--portfolio",
        dest=P_PORTFOLIO,
        metavar="<portfolio>",
        help="Portfolio name",
        required=False,
    )
    cp.add_argument(
        "-a", "--app", dest=P_APP, metavar="<app>", help="App name", required=False
    )
    cp.add_argument(
        "-b",
        "--branch",
        dest=P_BRANCH,
        metavar="<branch>",
        help="Branch name",
        required=False,
    )
    cp.add_argument(
        "-v",
        "--build",
        dest=P_BUILD,
        metavar="<build>",
        help="Build name",
        required=False,
    )
    cp.add_argument(
        "--show",
        dest="show",
        action="store_true",
        help="Show the current configuration",
        required=False,
    )

    return {"configure": (description, update_core_config)}
