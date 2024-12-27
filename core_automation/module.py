"""
The Core Automation CLI module
"""

import os
import boto3
from botocore.exceptions import ClientError, ProfileNotFound

from core_framework.constants import ENV_CLIENT, ENV_CLIENT_NAME, ENV_AWS_PROFILE

from .cmdparser.cmdparser import CoreArgumentParser
from .configure import (
    get_configure_command,
    get_core_config_data,
    get_client_vars,
)
from .run import get_run_command
from .engine import get_engine_command
from .organization import get_organization_command
from .info import get_info_command
from .portfolio import get_portfolio_command
from ._version import __version__


# Commands are built during the parser configuration.
COMMANDS = {}


def get_client_value(args) -> str | None:
    """
    Return the argument value for -c, --client.  We need
    this value in order to lookup defaults for display in the Parser Help text.
    Otherwise, we could have just used standard parser logic.

    Args:
        args (list[str]): command line argument list

    Raises:
        ValueError: if no value is provided for -c or --client
        ValueError: if -c, --client, or environment variable CLIENT is not specified

    Returns:
        str: the value for CLIENT
    """

    # Note that the -c, and --client will OVERRIDE the enviroment variable
    c = None
    for i, arg in enumerate(args[:-1]):
        if arg in ("-c", "--client"):
            c = args[i + 1]
            os.environ[ENV_CLIENT] = c
            os.environ[ENV_CLIENT_NAME] = c
            return c

    # Check if the --client parameter isn't specified
    if ENV_CLIENT in os.environ and ENV_CLIENT_NAME not in os.environ:
        os.environ[ENV_CLIENT_NAME] = os.environ[ENV_CLIENT]
    if ENV_CLIENT_NAME in os.environ and ENV_CLIENT not in os.environ:
        os.environ[ENV_CLIENT] = os.environ[ENV_CLIENT_NAME]

    return os.environ.get(ENV_CLIENT, None)


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


def process_configuration(client: str, aws_profile: str = "default") -> dict:
    """
    Loads the client vars and sets all the environment variables to setup the environent
    """
    config_values = {"client": client, "aws_profile": aws_profile}

    def set_config(key, value):
        key = key.lower()
        set_env_if(key.upper(), value)
        if key not in config_values:
            config_values[key] = value

    if client is not None:
        for key, value in get_client_vars(client).items():
            set_config(key, value)
        for key, value in get_core_config_data(client).items():
            set_config(key, value)

    return config_values


def credetials_exist(profile_name: str) -> True:
    try:
        boto3.Session(profile_name=profile_name)
        return profile_name
    except ProfileNotFound:
        return None


def get_aws_profile(
    args: list[str], client: str, default_profile: str = "default"
) -> str:
    """Get the AWS Profile name for the parameters or environment variable AWS_PROFILE

    The AWS profile is used EVERYWHERE.  If it is not set, it will be set to 'default'

    It will be set to the CLIENT name if and only if it is not set and there exists a
    current AWS profile configration for the CLIENT name.  Otherwise, it will be set to 'default'

    Args:
        args (list[str]): The command line arguments.  Will check for --aws-profile option
        client (str): The 'client' name to set the AWS_PROFILE to if it is not set
        default_profile (str, optional): _description_. Defaults to "default".

    Raises:
        ValueError: if the AWS_PROFILE is not set and there is no valid profile for the client
        or credentials cannot be found

    Returns:
        str: The AWS_PROFILE name
    """

    # If the argument exists, then set the default AWS_PROFILE to the argument
    aws_profile = os.getenv(ENV_AWS_PROFILE, None)
    for i, arg in enumerate(args[:-1]):
        if arg in ("--aws-profile"):
            aws_profile = args[i + 1]

    if not aws_profile:
        if credetials_exist(client):
            aws_profile = client
        else:
            aws_profile = "default"
    else:
        if not credetials_exist(aws_profile):
            raise ValueError(
                f"{ENV_AWS_PROFILE} is '{aws_profile}' but it is not a valid profile in your AWS configuration."
            )

    os.environ[ENV_AWS_PROFILE] = aws_profile

    return aws_profile


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
    cc = os.getenv(ENV_CLIENT, None)
    if cc:
        msg = f"{ENV_CLIENT} environment variable is set to '{cc}'.  This will be used as the default --client option"
    else:
        msg = f"Make your life easy, set the {ENV_CLIENT} environment variable to use it for the --client option"

    client = get_client_value(args) or "default"
    aws_profile = get_aws_profile(args, client)

    core_parser = CoreArgumentParser(
        prog="core",
        usage="core [-c client] [--aws-profile profile] command [<args>]",
        commands_title="Available Core-Automation Commands",
    )

    all_config_values = process_configuration(client, aws_profile)
    core_parser.set_defaults(**all_config_values)

    core_parser.add_argument(
        "-c",
        "--client",
        help=f"Client alias name of the organization. Default: {client}\n{msg}",
        default=client,
        required=False,
    )
    core_parser.add_argument(
        "--aws-profile",
        help=f"Specify the AWS profile to use. Default: {aws_profile}\n"
        "Defaults to --client option if AWS_PROFILE environment variable is not set.",
        default=aws_profile,
        required=False,
    )

    command_parser = core_parser.add_custom_subparsers(
        dest="command", metavar="<command>"
    )

    COMMANDS.update(get_configure_command(command_parser))
    COMMANDS.update(get_run_command(command_parser))
    COMMANDS.update(get_engine_command(command_parser))
    COMMANDS.update(get_organization_command(command_parser))
    COMMANDS.update(get_info_command(command_parser))
    COMMANDS.update(get_portfolio_command(command_parser))

    if not client or client == "unknown":
        core_parser.print_help()
        raise ValueError(
            "No client specified.  Please use -c or --client to specify the client alias or set the environment variable CLIENT"
        )

    pargs = core_parser.parse_args(args)

    return vars(pargs)


def make_defaults(**kwargs):
    """populate the client_account information"""
    try:
        session = boto3.Session()
        sts = session.client("sts")
        identity_information = sts.get_caller_identity()
        kwargs["client_account"] = identity_information.get("Account")
        kwargs["user_id"] = identity_information.get("UserId")
        kwargs["user_arn"] = identity_information.get("Arn")
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
    return "core", "Core Automation Module", __version__
