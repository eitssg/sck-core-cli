from ..cmdparser.cmdparser import ExecuteCommandsType

from .portfolios import get_portfolios_command
from .clients import get_clients_command
from .zones import get_zones_command
from .apps import get_apps_command

COMMAND: ExecuteCommandsType = {}


def get_description():
    return """
Manage context or FACTS database of client, portfolio, zone, and apps registrations.

Context   == FACTS database
Client    == AWS Organization
Zone      == A place in an AWS Account with a list of available regions
Portfolio == Business Application

"""


def get_context_command(subparsers) -> ExecuteCommandsType:
    """add the context parser"""
    description = "Manage context or FACTS database of client, portfolio, zone, and apps registrations."
    parser = subparsers.add_parser(
        "context",
        description=get_description(),
        choices=COMMAND,
        help=description,
    )

    parser.set_group_title(0, "Avalable Context actions")
    parser.set_group_title(1, "Available Econtext options")

    actionsparser = parser.add_custom_subparsers(dest="section", metavar="<section>")

    COMMAND.update(get_clients_command(actionsparser))
    COMMAND.update(get_zones_command(actionsparser))
    COMMAND.update(get_portfolios_command(actionsparser))
    COMMAND.update(get_apps_command(actionsparser))

    return {"context": (description, execute_context)}


def execute_context(**kwargs):
    """Execute the context command"""
    action = kwargs.get("section", None)
    if action in COMMAND:
        COMMAND[action][1](**kwargs)
