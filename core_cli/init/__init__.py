import os
import core_framework as util
from core_framework.constants import (
    DD_PORTFOLIO,
    DD_APP,
    DD_BRANCH,
    DD_BUILD,
    DD_ENVIRONMENT,
    DD_CLIENT,
    DD_SCOPE,
    P_CLIENT,
    P_SCOPE,
    P_PORTFOLIO,
    P_APP,
    P_BRANCH,
    P_BUILD,
    P_ENVIRONMENT,
    CTX_CONTEXT
)

from core_cli.cmdparser import ExecuteCommandsType
from core_cli.common import get_input, cprint


def get_init_command(subparsers) -> ExecuteCommandsType:
    """Get the parser for the init command"""

    description = "Initialize the app folder for core subsystem"

    init_parser = subparsers.add_parser(
        "init",
        description=description,
        help=description,
    )
    init_parser.set_group_title(0, "Init actions")
    init_parser.set_group_title(1, "Available options")

    init_parser.add_argument(
        "-p",
        "--portfolio",
        dest=P_PORTFOLIO,
        metavar="<portfolio>",
        help="Portfolio name",
        required=True,
    )
    init_parser.add_argument(
        "-a",
        "--app",
        dest=P_APP,
        metavar="<app>",
        help="App name",
        required=True,
    )
    init_parser.add_argument(
        "-b",
        "--branch",
        dest=P_BRANCH,
        metavar="<branch>",
        help="Branch name",
        required=True,
    )
    init_parser.add_argument(
        "-n",
        "--build",
        dest=P_BUILD,
        metavar="<build>",
        help="Build number",
        required=True,
    )
    init_parser.add_argument(
        "-e",
        "--environment",
        dest=P_ENVIRONMENT,
        metavar="<environment>",
        help="Environment name",
        required=False,
    )

    return {"init": (description, execute_init)}


def execute_init(**kwargs):
    """Initialize the client vars for the specified client."""
    cprint("Initializing app folder\n", style="bold underline")

    if is_cdk_app():
        cprint("I see that you are initializing core automation in a CDK app")
        cprint(
            "This will create a core platform folder in the app folder and update your cdk.json file\n"
        )

        result = get_input("Do you want to continue?", ["Y", "n"], "y")
        if result == "n":
            cprint("Aborting", style="bold red")
            return

    create_core_folder(**kwargs)

    cprint("Done", style="bold green")


def is_cdk_app():
    """Check if the current folder is a CDK app"""
    return os.path.exists("cdk.json")


def create_core_folder(**kwargs):
    """Create the core folder"""
    os.makedirs("platform", exist_ok=True)
    os.makedirs("platform/components", exist_ok=True)
    os.makedirs("platform/files", exist_ok=True)
    os.makedirs("platform/vars", exist_ok=True)

    write_component_file(**kwargs)
    write_app_vars_file(**kwargs)
    write_files_files()

    if is_cdk_app():
        update_cdk_json(fn="cdk.json", **kwargs)
    else:
        update_cdk_json(fn="sck.json", **kwargs)


def update_cdk_json(**kwargs):
    """Update the cdk.json file"""
    fn = kwargs.get("fn", "sck.json")

    if os.path.exists(fn):
        with open(fn, "r") as f:
            data = util.read_json(f)
        if CTX_CONTEXT not in data:
            data[CTX_CONTEXT] = {}
        updated = True
    else:
        data = {CTX_CONTEXT: {}}
        updated = False

    context = data[CTX_CONTEXT]

    scope = kwargs.get(P_SCOPE) or util.get_automation_scope()
    client = kwargs.get(P_CLIENT) or util.get_client()
    portfolio = kwargs.get(P_PORTFOLIO, "")
    app = kwargs.get(P_APP, "")
    branch = kwargs.get(P_BRANCH, "dev")
    build = kwargs.get(P_BUILD, "1")

    prn = f"prn:{portfolio}:{app}:{branch}:{build}"

    context.update({
        DD_SCOPE: scope,
        DD_CLIENT: client,
        DD_PORTFOLIO: portfolio,
        DD_APP: app,
        DD_BRANCH: branch,
        DD_BUILD: build,
        DD_ENVIRONMENT: kwargs.get(P_ENVIRONMENT, ""),
        "prn": prn
    })

    with open(fn, "w") as f:
        util.write_json(data, f, 2)

    if updated:
        cprint(f"Updated context: {fn}")
    else:
        cprint(f"Created conext: {fn}")


def write_component_file(**kwargs):

    fn = "platform/components/application.yaml"
    if os.path.exists(fn):
        return

    scope = kwargs.get(P_SCOPE) or util.get_automation_scope()
    client = kwargs.get(P_CLIENT) or util.get_client()
    portfolio = kwargs.get(P_PORTFOLIO, "")
    app = kwargs.get(P_APP, "")
    branch = kwargs.get(P_BRANCH, "dev")
    build = kwargs.get(P_BUILD, "1")

    with open(fn, "w") as f:
        util.write_yaml(
            {
                "my-application-compnent-label": {
                    "type": "set the type of the component",
                    "properties": {
                        "description": "Component description",
                        "tags": {
                            "Name": "my-application-compnent",
                            DD_SCOPE: scope,
                            DD_CLIENT: client,
                            DD_PORTFOLIO: portfolio,
                            DD_APP: app,
                            DD_BRANCH: branch,
                            DD_BUILD: build,
                        },
                    },
                },
            },
            f,
        )


def write_app_vars_file(**kwargs):

    fn = "platform/vars/vars.yaml"
    if os.path.exists(fn):
        return

    scope = kwargs.get(P_SCOPE) or util.get_automation_scope()
    client = kwargs.get(P_CLIENT) or util.get_client()
    portfolio = kwargs.get(P_PORTFOLIO, "")
    app = kwargs.get(P_APP, "")
    branch = kwargs.get(P_BRANCH, "dev")
    build = kwargs.get(P_BUILD, "1")

    prn = f"prn:{portfolio}:{app}:{branch}:{build}"

    with open(fn, "w") as f:
        util.write_yaml(
            {
                "default": {
                    P_SCOPE: scope,
                    P_CLIENT: client,
                    P_PORTFOLIO: portfolio,
                    P_APP: app,
                    P_BRANCH: branch,
                    P_BUILD: build,
                    "prn": prn,
                },
                "prod": {
                    P_BRANCH: "prod",
                },
                "nonprod": {
                    P_BRANCH: "nonprod",
                },
                "master": {
                    P_BRANCH: "master",
                },
                "dev": {
                    P_BRANCH: "dev",
                },
            },
            f,
        )


def write_files_files():
    fn = "platform/files/.keep"
    if os.path.exists(fn):
        return
    with open(fn, "w") as f:
        f.write("# This file is here to keep the files folder in git\n")
