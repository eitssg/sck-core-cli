""" load files from the client configuration file """

import os
from typing import Optional
import yaml


def find_folder(folder_name: str, start_path: str = ".") -> Optional[str]:
    """
    Find the folder with the specified name in the current directory tree UPWARDS
    for all parent folders until it's found
    """
    current_path = os.path.abspath(start_path)
    while True:
        potential_folder = os.path.join(current_path, folder_name)
        if os.path.isdir(potential_folder):
            return potential_folder
        parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
        if current_path == parent_path:
            return None
        current_path = parent_path


def load_yaml_file(file_path: str) -> dict:
    """Load the client_vars.yaml file"""
    with open(file_path, "r", encoding="utf8") as file:
        return yaml.safe_load(file)


def get_client_config_file(client: str, filename: str) -> dict:
    """Return the contents of the filename as a dictionary"""
    folder_name = f"{client}-config"
    config_folder = find_folder(folder_name)
    try:
        if config_folder:
            yaml_file_path = os.path.join(config_folder, filename)
            if os.path.isfile(yaml_file_path):
                return load_yaml_file(yaml_file_path)
        return {}
    except IOError as e:
        raise ValueError(
            f"Could not load the file {filename} from the "
            f"client configuration folder {config_folder}"
        ) from e
