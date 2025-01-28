"""
Core Automation application entry points
"""

from typing import Callable
import os
import sys

from botocore.exceptions import ClientError, ProfileNotFound  # noqa: E402

from dotenv import load_dotenv

import core_framework as util  # noqa: E402
from core_framework.constants import (  # noqa: E402
    ENV_CLIENT,
    P_IDENTITY,
    P_CLIENT,
    P_AWS_PROFILE,
    P_CORRELATION_ID
)

import core_helper.aws as aws  # noqa: E402

# Presently core_db requires the environment variables to be loaded.  It's initialized as part of loading the core_cli module.
load_dotenv(override=True)

# Please note that core_cli requires initial environment variables to be set.  Really only core_db needs it, but....
from core_cli.cmdparser.cmdparser import CoreArgumentParser  # noqa: E402
from core_cli.run import get_run_command  # noqa: E402
from core_cli.engine import get_engine_command  # noqa: E402
from core_cli.organization import get_organization_command  # noqa: E402
from core_cli.context import get_context_command  # noqa: E402
from core_cli.info import get_info_command  # noqa: E402
from core_cli.bootstrap import get_bootstrap_command  # noqa: E402
from core_cli.init import get_init_command  # noqa: E402
from core_cli.domain import get_domain_command  # noqa: E402

from core_cli._version import __version__  # noqa: E402

from core_cli.environment import set_environment  # noqa: E402


# Commands are built during the parser configuration.
COMMANDS: dict[str, tuple[str, Callable]] = {}


def parse_args(args: list[str], common_parser=None) -> dict:
    """
    Parse the arguments for this module.  The main CLI will pass the arguments
    to this module.  The result is expected from the argparse libary
    :param args: list of arguments for this module
    :return: the parameters parsed into the namespace
    """
    # Load the configuration file and set environment variables for all config daa
    # whether they are in ../client-config/client-vars.yaml or ~/.core/config

    # We are doing this only to check if CLIENT environment variable is set.  For 'msg' generation below
    client = util.get_client()
    aws_profile = util.get_aws_profile()

    if ENV_CLIENT in os.environ:
        msg = f"{ENV_CLIENT} environment variable is set to '{client}'.  This will be used as the default --client option"
    elif aws_profile:
        msg = f"AWS Session set to '{aws_profile}'.  This will be used as the default --client option"
        client = aws_profile
    else:
        msg = f"Make your life easy, set the {ENV_CLIENT} environment variable to avoid the need for the --client option"

    core_parser = CoreArgumentParser(
        prog="core",
        commands_title="Available Core-Automation Commands",
    )

    core_parser.add_argument(
        "-c",
        "--client",
        dest=P_CLIENT,
        metavar="<name>",
        help=f"Client alias name of the organization. Default: {client}\n{msg}",
        default=client,
        required=False,
    )
    core_parser.add_argument(
        "--aws-profile",
        dest=P_AWS_PROFILE,
        metavar="<profile>",
        help=f"Specify the AWS profile to use. Default: {aws_profile}\n"
        "Defaults to --client option if AWS_PROFILE environment variable is not set.",
        default=aws_profile,
        required=False,
    )

    command_parser = core_parser.add_custom_subparsers(
        dest="command", metavar="<module>"
    )

    # COMMANDS.update(get_configure_command(command_parser))
    COMMANDS.update(get_run_command(command_parser))
    COMMANDS.update(get_engine_command(command_parser))
    COMMANDS.update(get_organization_command(command_parser))
    COMMANDS.update(get_info_command(command_parser))
    COMMANDS.update(get_context_command(command_parser))
    COMMANDS.update(get_bootstrap_command(command_parser))
    COMMANDS.update(get_init_command(command_parser))
    COMMANDS.update(get_domain_command(command_parser))

    pargs = vars(core_parser.parse_args(args))

    if pargs.get(P_CLIENT) is None:
        pargs[P_CLIENT] = pargs.get(P_AWS_PROFILE)
    if pargs.get(P_CLIENT) is None:
        raise ValueError("The paramter --client is required.")

    return pargs


def add_current_user_to_data(data):
    """populate the client_account information"""
    try:

        data[P_CORRELATION_ID] = util.get_correlation_id()
        data[P_IDENTITY] = aws.get_identity()

    except ProfileNotFound as e:
        raise ValueError(
            f'(AWS_PROFILE) {e}.  Run the CLI "aws configure" and "aws sso configure"'
        ) from e

    except ClientError as e:
        raise ValueError(f"Error getting account information: {e}") from e


def execute(**kwargs) -> None:
    """
    Execute the specified command.

    :param kwargs: The parameters and other configuration data.
    :raises ValueError: If no client is specified or the command is not found.
    :return: None
    """
    add_current_user_to_data(kwargs)

    set_environment(kwargs)

    command = kwargs.get("command")
    if command in COMMANDS:
        COMMANDS[command][1](**kwargs)


def register_module(**kwargs) -> tuple[str, str, str]:
    """
    Initialize module using the parameters specified
    :param kwargs: Keyword Arguments of CLI definitions and other initialization data
    :return: the name and description of the module for "help" response
    """
    return "core", "Simple Cloud Kit Core CLI", __version__


def core_module(args):
    """
    This is the main entry point for the 'core' command when not run within
    the SCK.  This function duplicates what the SCK will do.  If you are using core.exe executable,
    this will run.  If you have installed the sck-mod-core package in your python SCK environment,
    then the SCK will call the three functions in the sck_mod_core module.

    Args:
        args (list): command-line arguments
    """
    try:

        registration_data = {
            "name": "SCK",
            "description": "SCK Autmation Engine",
            "version": __version__,
        }

        name, description, version = register_module(**registration_data)

        data = parse_args(args)

        data["module"] = {"name": name, "description": description, "version": version}
        data["sck"] = registration_data

        execute(**data)

    except KeyboardInterrupt:
        print("Aborted by user.")
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """
    This is the main entry point for the script within the python
    enviroment.  Used during pip install to create the commend 'core'
    """
    core_module(sys.argv[1:])


if __name__ == "__main__":
    main()
