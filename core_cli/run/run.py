""" Handle the run command for the Core Automation subsystem """

import os
import re
from typing import Callable

from core_framework.constants import (
    ENV_TASKS,
    ENV_PORTFOLIO,
    ENV_APP,
    ENV_BRANCH,
    ENV_BUILD,
    ENV_SCOPE,
    ENV_AUTOMATION_TYPE,
    ENV_BUCKET_NAME,
    ENV_BUCKET_REGION,
    ENV_INVOKER_LAMBDA_NAME,
    ENV_INVOKER_LAMBDA_REGION,
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
    client = data.get("client", None)

    aws_profile = data.get("aws_profile", None)
    if not aws_profile:
        data["aws_profile"] = os.getenv("AWS_PROFILE", client)

    scope_prefix = data.get("scope_prefix", "")
    bucket_name = data.get("bucket_name", None)
    if not bucket_name:
        bucket_region = data.get("bucket_region", None)
        data["bucket_name"] = f"{scope_prefix}{client}-core-automation-{bucket_region}"

    # Is there a bug here?  If the default invoker branch when not specified is 'master', does it need
    # to align to an invoker name that has been explicity specified?
    invoker_branch = data.get("invoker_branch", "master")
    data["invoker_branch"] = invoker_branch

    if invoker_branch == "master":
        data.setdefault("invoker_name", f"{scope_prefix}core-automation-master-invoker")
    else:
        invoker_branch_short_name = re.sub(r"[^a-z0-9\-]", "-", invoker_branch.lower())[
            :20
        ].rstrip("-")
        data["invoker_name"] = (
            f"{scope_prefix}core-automation-{invoker_branch_short_name}-invoker"
        )

    return data


def get_run_command(subparsers) -> dict:
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
        usage="core run [<tasks>] [<options>]",
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

    master_region = os.getenv("MASTER_REGION", "ap-southeast-1")
    scope_prefix = os.getenv("SCOPE_PREFIX", os.getenv("SCOPE_PREFIX", ""))

    client = os.getenv("CLIENT")
    aws_profile = os.getenv("AWS_PROFILE")

    run_parser.add_argument(
        "-c",
        "--client",
        default=client,
        help=f"Client name, used for resource prefixes. Default: {client}",
    )
    run_parser.add_argument("-s", "--scope", default=scope_prefix, help="Scope name")
    run_parser.add_argument(
        "-p", "--portfolio", default=os.getenv("PORTFOLIO"), help="Portfolio name"
    )
    run_parser.add_argument("-a", "--app", default=os.getenv("APP"), help="App name")
    run_parser.add_argument(
        "-b", "--branch", default=os.getenv("BRANCH"), help="Branch name"
    )
    run_parser.add_argument(
        "-n", "--build", default=os.getenv("BUILD"), help="Build name"
    )
    run_parser.add_argument(
        "--aws-profile",
        default=aws_profile,
        help=f"AWS profile name. Default: {aws_profile}",
    )
    run_parser.add_argument(
        "--bucket-name", default=os.getenv("BUCKET_NAME"), help="S3 bucket name"
    )
    run_parser.add_argument(
        "--bucket-region",
        default=os.getenv("BUCKET_REGION", master_region),
        help=f'S3 bucket region. Default "{master_region}"',
    )
    run_parser.add_argument(
        "--automation-type",
        default=os.getenv("AUTOMATION_TYPE", "pipeline"),
        choices=["deployspec", "pipeline"],
        help='Automation type [deployspec, pipeline].  Default: "pipeline"',
    )
    run_parser.add_argument(
        "--extra-facts-json",
        metavar="",
        help="Supply extra facts to the compiler. Must be a valid json string.",
    )
    run_parser.add_argument(
        "--invoker-name",
        default=os.getenv("INVOKER_LAMBDA_NAME"),
        help="Invoker Lambda name",
    )
    run_parser.add_argument(
        "--invoker-branch",
        default=os.getenv("INVOKER_LAMBDA_BRANCH"),
        help="Invoker Lambda branch. Takes precedence over the --invoker-name option.",
    )
    run_parser.add_argument(
        "--invoker-region",
        default=os.getenv("INVOKER_LAMBDA_REGION", master_region),
        help=f'Invoker Lambda region, default "{master_region}"',
    )
    run_parser.add_argument(
        "--automation-account",
        default=os.getenv("AUTOMATION_ACCOUNT"),
        help="Automaton AWS Account ID",
    )
    run_parser.add_argument(
        "--organization_account",
        default=os.getenv("ORGANIZATION_ACCOUNT"),
        help="Master/Payer Organization Account",
    )
    run_parser.add_argument(
        "--organization_id",
        default=os.getenv("ORGANIZATION_ID"),
        help="AWS Organization ID",
    )
    run_parser.add_argument(
        "--master-region",
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
