import configparser
import os
from argparse import ArgumentParser


def get_client_name(**kwargs) -> str:
    client = kwargs.get("client")
    if not client:
        raise OSError("You must specify 'client'. No client specified")
    return client


def load_config(**kwargs) -> configparser.ConfigParser:

    client = get_client_name(**kwargs)

    # Define the config file and directory
    config_dir = os.path.expanduser("~/.core")
    config_file = os.path.join(config_dir, "config")

    # Create the directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    # Initialize the config parser
    config = configparser.ConfigParser()

    # Load the config file if it exists, otherwise create it
    if os.path.exists(config_file):
        config.read(config_file)
    else:
        config[client] = {}

    if not config.has_section(client):
        config.add_section(client)

    return config


def add_command(parser: ArgumentParser) -> ArgumentParser:
    """
    Add the parameters for the 'configure' command to the parser.

    @param parser: The parser to add the parameters to
    """
    p = parser.add_subparsers(
        title="Configuations", help="Configure the Core-Automation client"
    )
    sp = p.add_parser("configure", help="Configure the Core-Automation client")
    sp.add_argument("--delete", help="Delete the service")

    return parser


def configure(**kwargs) -> bool:
    """
    Configure Core-Automation to run in the local environment.
    These values are the same as the 'client_vars.yaml" file and
    can be configured so you don't need to checkout the cilent-config.git repository

    @return: True if the configuration was successful, False otherwise
    """
    try:
        config_file = os.path.expanduser("~/.core/config")

        client = get_client_name(**kwargs)

        config = load_config(**kwargs)

        # Prompt the user for each piece of information
        prompts = [
            ("Automation account number", "automation_account"),
            ("Organization account number", "organization_account"),
            ("Organization id", "organization_id"),
            ("Automation region", "automation_region"),
            ("Invoker region", "invoker_region"),
        ]

        for prompt, key in prompts:
            # Get the current value if it exists
            current_value = config[client].get(key, "")
            # Prompt the user for the new value
            new_value = input(f"{prompt} [{current_value}]: ")
            # If the user entered a new value, save it in the config file
            if new_value:
                config[client][key] = new_value

        # Write the updated config file back to disk
        with open(config_file, "w") as f:
            config.write(f)

        return True

    except IOError as e:
        print(f"Error configuring Core-Automation: {e}")
        return False
