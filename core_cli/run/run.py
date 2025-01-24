""" Handle the run command for the Core Automation subsystem """

import os
import re
from typing import Callable
from ..cmdparser import ExecuteCommandsType

from core_framework.constants import (
    ENV_AWS_PROFILE,
    ENV_TASKS,
    ENV_PORTFOLIO,
    ENV_APP,
    ENV_BRANCH,
    ENV_BUILD,
    ENV_SCOPE,
    ENV_MASTER_REGION,
    ENV_AUTOMATION_TYPE,
    ENV_BUCKET_NAME,
    ENV_BUCKET_REGION,
    ENV_INVOKER_LAMBDA_NAME,
    ENV_INVOKER_LAMBDA_REGION,
    ENV_INVOKER_LAMBDA_ARN,
    ENV_AUTOMATION_ACCOUNT,
    ENV_ORGANIZATION_ACCOUNT,
    ENV_ORGANIZATION_ID,
    P_SCOPE,
    P_CLIENT,
    P_AWS_PROFILE,
    P_PORTFOLIO,
    P_APP,
    P_BRANCH,
    P_BUILD,
    P_BUCKET_NAME,
    P_BUCKET_REGION,
    P_AUTOMATION_TYPE,
    P_INVOKER_NAME,
    P_INVOKER_ARN,
    P_INVOKER_REGION,
    P_AUTOMATION_ACCOUNT,
    P_ORGANIZATION_ACCOUNT,
    P_ORGANIZATION_ID,
    P_MASTER_REGION,
    V_DEFAULT_REGION,
    V_DEPLOYSPEC,
    V_PIPELINE,
)

from .apply import task_apply
from .package import task_package
from .upload import task_upload
from .compile import task_compile
from .plan import task_plan
from .deploy import task_deploy
from .release import task_release
from .teardown import task_teardown


TASKS: dict[str, tuple[str, Callable[..., None]]] = {
    "package": ("Package application files (platform/package.sh)", task_package),
    "upload": ("Upload the package to the S3 bucket for deployment", task_upload),
    "compile": ("Compile the application and generate Actions", task_compile),
    "plan": ("Plan a deployment.  Must follow with apply", task_plan),
    "apply": ('Apply a deployment plan. Instead of "deploy"', task_apply),
    "deploy": ("Execute the application Actions", task_deploy),
    "release": ("Release the deployed application", task_release),
    "teardown": ("Teardown the deployed application", task_teardown),
}


def get_epilog():
    return f"""Options can also be set via environment variables:
    {ENV_TASKS}
    {ENV_PORTFOLIO}, {ENV_APP}, {ENV_BRANCH}, {ENV_BUILD}
    {ENV_SCOPE}
    {ENV_AUTOMATION_TYPE}
    {ENV_BUCKET_NAME}, {ENV_BUCKET_REGION}
    {ENV_INVOKER_LAMBDA_NAME}, {ENV_INVOKER_LAMBDA_REGION}
"""


def make_defaults(data: dict) -> dict:
    """Make default values that were not supplied in the command line arguments"""

    # This can't poossibly be None.  The program will fail long before it gets here if it is.
    client = data.get(P_CLIENT, None)

    aws_profile = data.get(P_AWS_PROFILE, None)
    if not aws_profile:
        data[P_AWS_PROFILE] = os.getenv(ENV_AWS_PROFILE, client)

    scope_prefix = data.get(P_SCOPE, "")
    bucket_name = data.get(P_BUCKET_NAME, None)
    if not bucket_name:
        bucket_region = data.get(P_BUCKET_REGION, None)
        data[P_BUCKET_NAME] = f"{scope_prefix}{client}-core-automation-{bucket_region}"

    # Is there a bug here?  If the default invoker branch when not specified is 'master', does it need
    # to align to an invoker name that has been explicity specified?
    invoker_branch = data.get("invoker_branch", "master")
    data["invoker_branch"] = invoker_branch

    if invoker_branch == "master":
        data.setdefault(P_INVOKER_NAME, f"{scope_prefix}core-automation-master-invoker")
    else:
        invoker_branch_short_name = re.sub(r"[^a-z0-9\-]", "-", invoker_branch.lower())[
            :20
        ].rstrip("-")
        data[P_INVOKER_NAME] = (
            f"{scope_prefix}core-automation-{invoker_branch_short_name}-invoker"
        )

    return data


def get_run_command(subparsers) -> ExecuteCommandsType:
    """
    Add the run parser to the Core Automation commntds
    """

    descriptions = "Run the Core Automation subsystem tasks (package, upload, compile, plan, apply, deploy, release, teardown)"

    default_commands = ["package", "upload", "compile", "deploy"]

    run_parser = subparsers.add_parser(
        "run",
        choices=TASKS,
        description=descriptions,
        epilog=get_epilog(),
        help=descriptions,
    )

    run_parser.set_group_title(0, "Available tasks")
    run_parser.set_group_title(1, "Available options")

    run_parser.add_argument(
        "tasks",
        nargs="+",
        choices=TASKS.keys(),
        metavar="<tasks>",
        default=default_commands,
    )

    master_region = os.getenv(ENV_MASTER_REGION, V_DEFAULT_REGION)
    scope_prefix = os.getenv(ENV_SCOPE, os.getenv("SCOPE_PREFIX", ""))

    run_parser.add_argument("-s", "--scope", default=scope_prefix, help="Scope name")
    run_parser.add_argument(
        "-p",
        "--portfolio",
        dest=P_PORTFOLIO,
        metavar="<portfolio>",
        default=os.getenv(ENV_PORTFOLIO),
        help="Portfolio name",
    )
    run_parser.add_argument(
        "-a",
        "--app",
        dest=P_APP,
        metavar="<app>",
        default=os.getenv(ENV_APP),
        help="App name",
    )
    run_parser.add_argument(
        "-b",
        "--branch",
        dest=P_BRANCH,
        metavar="<branch>",
        default=os.getenv(ENV_BRANCH),
        help="Branch name",
    )
    run_parser.add_argument(
        "-n",
        "--build",
        dest=P_BUILD,
        metavar="<build>",
        default=os.getenv(ENV_BUILD),
        help="Build name",
    )
    run_parser.add_argument(
        "--bucket-name",
        dest=P_BUCKET_NAME,
        metavar="<bucket-name>",
        default=os.getenv(ENV_BUCKET_NAME),
        help="S3 bucket name",
    )
    run_parser.add_argument(
        "--bucket-region",
        dest=P_BUCKET_REGION,
        metavar="<bucket-region>",
        default=os.getenv(ENV_BUCKET_REGION, master_region),
        help=f'S3 bucket region. Default "{master_region}"',
    )
    run_parser.add_argument(
        "--automation-type",
        dest=P_AUTOMATION_TYPE,
        metaavar="<automation-type>",
        default=os.getenv(ENV_AUTOMATION_TYPE, V_PIPELINE),
        choices=[V_DEPLOYSPEC, V_PIPELINE],
        help=f'Automation type [{V_DEPLOYSPEC}, {V_PIPELINE}].  Default: "{V_PIPELINE}"',
    )
    run_parser.add_argument(
        "--invoker-name",
        dest=P_INVOKER_NAME,
        metavar="<invoker-name>",
        default=os.getenv(ENV_INVOKER_LAMBDA_NAME),
        help="Invoker Lambda name",
    )
    run_parser.add_argument(
        "--invoker-arn",
        dest=P_INVOKER_ARN,
        metavar="<invoker-arn>",
        default=os.getenv(ENV_INVOKER_LAMBDA_ARN),
        help="Invoker Lambda branch. Takes precedence over the --invoker-name option.",
    )
    run_parser.add_argument(
        "--invoker-region",
        dest=P_INVOKER_REGION,
        metavar="<invoker-region>",
        default=os.getenv(ENV_INVOKER_LAMBDA_REGION, master_region),
        help=f'Invoker Lambda region, default "{master_region}"',
    )
    run_parser.add_argument(
        "--automation-account",
        dest=P_AUTOMATION_ACCOUNT,
        metavar="<automation-account>",
        default=os.getenv(ENV_AUTOMATION_ACCOUNT),
        help="Automaton AWS Account ID",
    )
    run_parser.add_argument(
        "--organization_account",
        dest=P_ORGANIZATION_ACCOUNT,
        metavar="<organization-account>",
        default=os.getenv(ENV_ORGANIZATION_ACCOUNT),
        help="Master/Payer Organization Account",
    )
    run_parser.add_argument(
        "--organization_id",
        dest=P_ORGANIZATION_ID,
        metavar="<organization-id>",
        default=os.getenv(ENV_ORGANIZATION_ID),
        help="AWS Organization ID",
    )
    run_parser.add_argument(
        "--master-region",
        dest=P_MASTER_REGION,
        metavar="<master-region>",
        default=master_region,
        help="AWS region for the master Automation account",
    )
    run_parser.add_argument(
        "--force",
        action="store_true",
        help="Set to 'true' to force through an action if it "
        "has protection checks on it -- see teardown.",
    )

    return {"run": (descriptions, execute_run)}


def execute_run(**kwargs):
    """Run the Core Automation tasks"""

    data = make_defaults(dict(kwargs))

    tasks = kwargs.get("tasks", [])
    for task in tasks:
        if task in TASKS:
            TASKS[task][1](**data)
