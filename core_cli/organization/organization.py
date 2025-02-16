"""Manage the organization accounts"""

from ..cmdparser import ExecuteCommandsType

from .user import get_user_tasks
from .scp import get_scp_tasks
from .org_units import get_org_unit_tasks
from .show import get_show_tasks
from .control_tower import get_control_tower_tasks

TASKS: ExecuteCommandsType = {}


def execute_organization(**kwargs):
    """Configure the client vars for the specified client."""
    task = kwargs.get("tasks")
    if task in TASKS:
        TASKS[task][1](**kwargs)
    else:
        print(f"Task {task} not found")


def get_organization_command(subparsers) -> ExecuteCommandsType:
    """Get the parser for the configuration command"""

    DESCRPTION = "Manage the organization and child account"

    org_parser = subparsers.add_parser(
        "org",
        description=DESCRPTION,
        help=DESCRPTION,
    )
    org_parser.set_group_title(0, "Org Actions")
    org_parser.set_group_title(1, "Available Options")

    subparsers = org_parser.add_custom_subparsers(
        dest="tasks", metavar="<task>", help="sub-command help"
    )

    TASKS.update(get_user_tasks(subparsers))
    TASKS.update(get_show_tasks(subparsers))
    TASKS.update(get_scp_tasks(subparsers))
    TASKS.update(get_org_unit_tasks(subparsers))
    TASKS.update(get_control_tower_tasks(subparsers))

    return {"org": (DESCRPTION, execute_organization)}
