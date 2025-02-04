"""load files from the client configuration file"""

import os
from typing import Optional
import core_framework as util
from core_framework.constants import (
    CTX_CONTEXT,
    P_CLIENT,
    P_PORTFOLIO,
    P_APP,
    P_BRANCH,
    P_BUILD,
)

from ..apiclient import APIClient

api_client = APIClient.get_instance()


def find_file(file_names: list[str], start_path: str = ".") -> Optional[str]:
    """
    Find the first match of file_names in the current folder.  If nto found, then
    search the parent folder and continue until one file is found or ther are no more
    parents
    """
    for root, _, files in os.walk(start_path):
        for file_name in file_names:
            if file_name in files:
                return os.path.join(root, file_name)
        parent = os.path.dirname(root)
        if parent:
            result = find_file(file_names, parent)
            if result:
                return result
    return None


def load_context_client(data: dict) -> dict:
    """load the context from the facts API /v1/facts/{client} using the APIClient object"""

    client = data.get(P_CLIENT, "")
    portfolio = data.get(P_PORTFOLIO, "")
    app = data.get(P_APP, "")
    branch = data.get(P_BRANCH, "")
    build = data.get(P_BUILD, "")
    prn = f"prn:{portfolio}:{app}:{branch}:{build}"

    params = {"prn": prn}

    result = api_client.get(f"/v1/facts/{client}", params=params)
    if result.status_code != 200:
        raise ValueError(f"Could not load the context for the client {client}")
    data = result.json()
    return {CTX_CONTEXT: data}


def load_context_file(file_path: str) -> dict:
    """Load the sdk.json or cdk.json file"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf8") as file:
            return util.read_json(file)
    return {"context": {}}


def get_client_config_file(data: dict) -> dict:
    """Return the contents of the filename as a dictionary"""
    file_names = ["cdk.json", "sdk.json"]
    file_path = find_file(file_names, os.getcwd())
    try:
        if file_path:
            context = load_context_file(file_path)
        else:
            context = load_context_client(data)
        if CTX_CONTEXT not in context:
            raise ValueError(
                "Could not find the context key in the client configuration"
            )
        return context[CTX_CONTEXT]
    except IOError as e:
        raise ValueError(
            "Could not load context file from the client configuration"
        ) from e
