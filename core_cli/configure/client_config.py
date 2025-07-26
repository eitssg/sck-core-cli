"""load files from the client configuration file"""

from typing import Any
import os

import core_framework as util
from core_framework.constants import CTX_CONTEXT, P_CLIENT

from ..apiclient import APIClient


def find_file(file_names: list[str], start_path: str = ".") -> str | None:
    """
    Find the first match of file_names in the current folder.  If nto found, then
    search the parent folder and continue until one file is found or ther are no more
    parents
    """
    path = os.path.abspath(start_path)
    for file_name in file_names:
        if os.path.exists(os.path.join(path, file_name)):
            return os.path.join(path, file_name)
    parent = os.path.dirname(path)
    if parent and parent != path:
        return find_file(file_names, parent)
    return None


def load_context_client(args: dict[str, str | None]) -> dict[str, Any]:
    """load the context from the facts API /v1/facts/{client} using the APIClient object"""

    client = args.get(P_CLIENT, "")

    api_client = APIClient.get_instance()
    headers = api_client.get_headers(args)

    result = api_client.get(f"/api/v1/registry/client/{client}", headers=headers)

    json_result = result.json()
    context = json_result.get("data", {})
    if result.status_code != 200:
        error = context.get("message", "Unknown error")
        raise ValueError(f"Could not load the context for the client {client}. {error}")
    return {CTX_CONTEXT: context}


def load_context_file(file_path: str) -> dict[str, Any]:
    """Load the sdk.json or cdk.json file"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf8") as file:
            return util.read_json(file)
    return {CTX_CONTEXT: {}}


def get_client_context(data: dict) -> dict:
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
