""" This module manages the engine tasks """

from ..cmdparser import ExecuteCommandsType

from .deploy import add_deploy_parser
from .zones import add_zones_parser
from .clean import add_clean_parser
from .vpc import add_vpc_parser
from .init import add_init_parser
from .app import add_app_parser
from .source import add_source_parser
from .database import add_db_management_parser
from .teardown import add_teardown_parser
from .info import add_info_parser

# Tasks are built in the parser generation
TASKS = {}


def get_engine_command(subparsers) -> ExecuteCommandsType:
    """create the engine command parer"""

    description = "Engine service deployment commands"

    engine_parser = subparsers.add_parser(
        "engine",
        description=description,
        help=description,
    )
    engine_parser.set_group_title(0, "Engine tasks")
    engine_parser.set_group_title(1, "Available options")

    task_parsers = engine_parser.add_custom_subparsers(dest="tasks", metavar="<task>")

    # Initialize the core automation platform
    TASKS.update(add_init_parser(task_parsers))

    TASKS.update(add_deploy_parser(task_parsers))
    TASKS.update(add_zones_parser(task_parsers))
    TASKS.update(add_clean_parser(task_parsers))
    TASKS.update(add_vpc_parser(task_parsers))
    TASKS.update(add_app_parser(task_parsers))
    TASKS.update(add_source_parser(task_parsers))
    TASKS.update(add_db_management_parser(task_parsers))
    TASKS.update(add_teardown_parser(task_parsers))
    TASKS.update(add_info_parser(task_parsers))

    return {"engine": (description, execute_engine)}


def execute_engine(**kwargs):
    """execute the engine task"""

    task = kwargs.get("tasks")

    if task in TASKS:
        TASKS[task][1](**kwargs)
