""" Configuration Module Package """

import os
from .core_config import update_core_config


def execute_configure(**kwargs):
    """Configure the client vars for the specified client."""
    update_core_config(**kwargs)


def get_configure_command(subparsers):
    """Get the parser for the configuration command"""

    description = "Configure the core subsystem client vars"

    client = os.getenv("CLIENT", None)
    aws_profile = os.getenv("AWS_PROFILE", "default")

    config_parser = subparsers.add_parser(
        "configure",
        description=description,
        usage="core configure [--client <name>] [--show] [--delete]",
        help=description,
    )
    config_parser.set_group_title(0, "Configure actions")
    config_parser.set_group_title(1, "Available options")

    config_parser.add_argument(
        "-c",
        "--client",
        required=client is None,
        help=f"Client alias name of the organization. Default: {client}",
        default=client,
    )
    config_parser.add_argument(
        "--aws-profile",
        required=False,
        help=f"AWS profile to use to access automation engine. default {aws_profile}",
        default=aws_profile,
    )
    config_parser.add_argument(
        "-s", "--show", help="Show the current configuration", action="store_true"
    )
    config_parser.add_argument(
        "-r",
        "--delete",
        help="Delete the configuration specified in --client",
        action="store_true",
    )

    return {"configure": (description, execute_configure)}
