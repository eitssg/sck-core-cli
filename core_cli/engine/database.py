
import core_framework as util

from core_framework.models import TaskPayload

from core_deployspec import compiler
from core_invoker import invoke

from .._version import __version__
from ..cmdparser import ExecuteCommandsType

from ..common import get_input, cprint

from .common import exexecution_check


TASK: ExecuteCommandsType = {}


def add_db_management_parser(subparsers) -> ExecuteCommandsType:
    """Add the DB management parser"""

    description = "API DB Managment"

    subparser = subparsers.add_parser(
        "database",
        description=description,
        help=description,
    )
    subparser.set_group_title(0, "Migrate tasks")
    subparser.set_group_title(1, "Available options")

    task_parsers = subparser.add_custom_subparsers(dest="task", metavar="<task>")

    TASK.update(get_deploy_task(task_parsers))
    TASK.update(get_teardown_task(task_parsers))

    return {"database": (description, execute_database)}


def execute_database(**kwargs):
    """execute the command"""

    task = kwargs.get("task")
    if task in TASK:
        TASK[task][1](**kwargs)
    else:
        print(f"Task {task} not found")


def get_deploy_task(parsers) -> ExecuteCommandsType:
    """add the deploy parser"""

    description = "Deploy the Database"

    subparser = parsers.add_parser(
        "deploy",
        description=description,
        help=description,
    )
    subparser.set_group_title(0, "Deploy actions")
    subparser.set_group_title(1, "Available options")

    return {"deploy": (description, execute_deploy)}


def execute_deploy(**kwargs):
    """execute the command"""

    exexecution_check(kwargs)

    kwargs["portfolio"] = "simple-cloud-kit"
    kwargs["app"] = "db"
    kwargs["branch"] = "simple-cloud-kit"
    kwargs["build"] = __version__

    task_payload = TaskPayload.from_arguments(**kwargs)

    print_task_payload(task_payload)

    result = get_input("Is this the account you want to deploy to? ", ["y", "n"])
    if result == "n":
        cprint("Exiting")
        return

    # STEP 1 - Package
    create_package(kwargs)

    # STEP 2 - Upload
    upload_package(kwargs)

    # STEP 3 - Compile
    compile_package(kwargs)

    # STEP 4 - Deploy
    deploy_package(kwargs)

    cprint("Deploy")


def print_task_payload(task_payload: TaskPayload):
    cprint("Deployment Information:")

    deployment_info = task_payload.DeploymentDetails
    cprint(f"   Client Name: {deployment_info.Client}")
    cprint(f"   Portfolio BizApp: {deployment_info.Portfolio}")
    cprint(f"   Application Name: {deployment_info.App}")
    cprint(f"   Branch: {deployment_info.Branch}")
    cprint(f"   Build: {deployment_info.Build}")


def create_package(kwargs):
    """create and upload the package"""

    kwargs['task'] = 'package'
    kwargs['automation_type'] = 'deployspec'
    task_payload = TaskPayload.from_arguments(**kwargs)

    cprint("Creating and uploading package")

    invoke(task_payload.model_dump())

def upload_package(kwargs):
    """upload the package"""

    kwargs['task'] = 'upload'
    kwargs['automation_type'] = 'deployspec'
    task_payload = TaskPayload.from_arguments(**kwargs)

    cprint("Uploading package")

def compile_package(kwargs):
    """compile the package"""

    kwargs['task'] = 'compile'
    kwargs['automation_type'] = 'deployspec'
    task_payload = TaskPayload.from_arguments(**kwargs)

    cprint("Compiling package")

    invoke(task_payload.model_dump())


def deploy_package(kwargs):
    """deploy the package"""

    kwargs['task'] = 'deploy'
    kwargs['automation_type'] = 'deployspec'
    task_payload = TaskPayload.from_arguments(**kwargs)

    cprint("Deploying package")

    invoke(task_payload.model_dump())

def get_teardown_task(subparsers) -> ExecuteCommandsType:
    """add the teardown parser"""

    description = "Teardown the Database"

    subparser = subparsers.add_parser(
        "teardown",
        usage="core engine migrate teardown [<options>]",
        description=description,
        help=description,
    )
    subparser.set_group_title(0, "Teardown actions")
    subparser.set_group_title(1, "Available options")

    return {"teardown": (description, execute_teardown)}


def execute_teardown(**kwargs):
    """execute the command"""

    exexecution_check(kwargs)

    print("Teardown")

    kwargs['task'] = 'teardown'
    kwargs['automation_type'] = 'deployspec'
    task_payload = TaskPayload.from_arguments(**kwargs)

    invoke(task_payload.model_dump())
