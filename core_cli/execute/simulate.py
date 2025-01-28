
import core_framework as util
from core_framework.constants import P_PORTFOLIO, P_APP, P_BRANCH, P_BUILD
from core_framework.models import TaskPayload
from core_cli.common import cprint

import core_helper.aws as aws

from core_execute.handler import handler as lambda_handler


def execute_event(event: dict) -> dict:
    """
    Execute the event in either local mode or in AWS lambda mode.
    """
    arn = "arn:aws:lambda:us-east-1:123456789012:function:core-execute"
    role = "CoreAutomationExecuteRole"

    if util.is_local_mode():
        result = lambda_handler(event)
    else:
        result = aws.invoke_lambda(arn, event, role=role)

    return result if result is not None else {}


def call_invoker(**kwargs):

    cprint("\nCalling Invoker")

    event = TaskPayload.from_arguments(**kwargs)

    event = execute_event(event)


def deploy(**kwargs):
    print("Deploying", style="bold underline")
    call_invoker(**kwargs)


def release(**kwargs):
    cprint("Releasing", style="bold underline")
    call_invoker(**kwargs)


def teardown(**kwargs):
    cprint("Tearing down", style="bold underline")
    call_invoker(**kwargs)


ACTIONS = {"deploy": deploy, "release": release, "teardown": teardown}


def get_execute_command(subparsers):

    description = "Execute Actions Runner"

    parser = subparsers.add_parser(
        "execute",
        description=description,
        help=description,
    )
    parser.set_group_title(0, "Execute actions")
    parser.set_group_title(1, "Available options")

    parser.add_argument(
        "task", metavar="<task>", choices=ACTIONS.keys(), help="Action to perform"
    )

    parser.add_argument(
        "-p",
        "--portfolio",
        dest=P_PORTFOLIO,
        metavar="<portfolio>",
        help="Portfolio name",
        required=True,
    )
    parser.add_argument(
        "-a",
        "--app",
        dest=P_APP,
        metavar="<app>",
        help="Application name",
        required=True,
    )
    parser.add_argument(
        "-b",
        "--branch",
        dest=P_BRANCH,
        metavar="<branch>",
        help="Branch name",
        required=True,
    )
    parser.add_argument(
        "-n",
        "--build",
        dest=P_BUILD,
        metavar="<build>",
        help="Build number",
        required=True,
    )

    return {"execute", (description, run_execute)}


def run_execute(**kwargs):

    task = kwargs.get("task", None)

    # Run the action
    if task in ACTIONS:
        ACTIONS[task][1](**kwargs)
