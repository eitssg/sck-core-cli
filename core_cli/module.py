"""
The Core Automation CLI module
"""

from typing import Callable
import os
from botocore.exceptions import ClientError, ProfileNotFound

import core_framework as util

from core_framework.constants import ENV_CLIENT
import core_helper.aws as aws

from .cmdparser.cmdparser import CoreArgumentParser
from .run import get_run_command
from .engine import get_engine_command
from .organization import get_organization_command
from .portfolio import get_portfolio_command
from .info import get_info_command
from .setup import get_setup_command

from ._version import __version__

from .environment import set_environment

# Commands are built during the parser configuration.
COMMANDS: dict[str, tuple[str, Callable]] = {}


def set_env_if(name: str, value: str):
    """
    Sets environment varable only if it's not already set.

    Args:
        name (str): key of the variable.  This will be set to upper() in this function.
        value (str): value for the variable
    """
    env_var = name.upper()

    # ONLY update environment variables if they are NOT already set in the environment
    if env_var not in os.environ:
        os.environ[env_var] = str(value)


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
        metavar="client",
        help=f"Client alias name of the organization. Default: {client}\n{msg}",
        default=client,
        required=False,
    )
    core_parser.add_argument(
        "--aws-profile",
        metavar="aws_profile",
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
    COMMANDS.update(get_portfolio_command(command_parser))
    COMMANDS.update(get_setup_command(command_parser))

    pargs = vars(core_parser.parse_args(args))

    if pargs.get("client") is None:
        pargs["client"] = pargs.get("aws_profile")
    if pargs.get("client") is None:
        raise ValueError("The paramter --client is required.")

    return pargs


def make_defaults(**kwargs):
    """populate the client_account information"""
    try:
        identity = aws.get_identity()

        kwargs["user"] = {
            "account": identity.get("Account"),
            "id": identity.get("UserId"),
            "arn": identity.get("Arn"),
        }
        return kwargs

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
    kwargs = make_defaults(**kwargs)

    set_environment(**kwargs)

    command = kwargs.get("command")
    if command not in COMMANDS:
        raise ValueError(f"Command {command} not found")

    COMMANDS[command][1](**kwargs)


def register_module(**kwargs) -> tuple[str, str, str]:
    """
    Initialize module using the parameters specified
    :param kwargs: Keyword Arguments of CLI definitions and other initialization data
    :return: the name and description of the module for "help" response
    """
    return "core", "Simple Cloud Kit Core CLI", __version__
