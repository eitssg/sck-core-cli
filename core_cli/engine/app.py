""" Module that process app management commands """

from ..cmdparser import ExecuteCommandsType


def action_describe(**kwargs):
    """describe the application"""
    print("Describe")


def action_find(**kwargs):
    """find the application"""
    print("Find")


def action_components(**kwargs):
    """list the application components"""
    print("Components")


def action_status(**kwargs):
    """list the application status"""
    print("Status")


ACTIONS: ExecuteCommandsType = {
    "describe": (
        "Reads JSON file from [stdin] and generates a stack description",
        action_describe,
    ),
    "find": (
        "Scan cloudformation stacks and build up a nested dictionary of names, typically portfolio-app-branch ",
        action_find,
    ),
    "components": (
        "Search cloudwatch logs for compiler to identify Consumables in use ",
        action_components,
    ),
    "status": (
        "Get the status of a deploying app (CloudFormation Status)",
        action_status,
    ),
}


def add_app_parser(subparsers) -> ExecuteCommandsType:
    """add the clean parser"""

    description = "Manage applications database / facts"

    subparser = subparsers.add_parser(
        "app",
        description=description,
        help=description,
    )
    subparser.set_group_title(0, "App actions")
    subparser.set_group_title(1, "Available options")

    action_parser = subparser.add_custom_subparsers(dest="action", metavar="<action>")
    for k, v in ACTIONS.items():
        action_parser.add_parser(k, help=v[0])

    return {"app": (description, execute_app)}


def execute_app(**kwargs):
    """execute the command"""
    action = kwargs.get("action", None)
    if action in ACTIONS:
        ACTIONS[action][1](**kwargs)
    else:
        print(f"Unknown action: {action}")
