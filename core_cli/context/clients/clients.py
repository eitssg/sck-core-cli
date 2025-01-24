from rich.table import Table
from rich import box
from fastapi.testclient import TestClient

from core_framework.constants import (
    P_CLIENT,
    P_CLIENT_REGION,
    P_ORGANIZATION_ID,
    P_ORGANIZATION_NAME,
    P_ORGANIZATION_ACCOUNT,
    P_ORGANIZATION_EMAIL,
    P_AUTOMATION_ACCOUNT,
    P_REGION,
)

from core_api.api import get_app

from ...common import cprint
from ...cmdparser import ExecuteCommandsType


api_client = TestClient(get_app())


def list_clients(**kwargs):
    """list clients"""

    cprint("\nList Clients\n", style="bold underline")

    response = api_client.get("/api/v1/registry/clients")
    rest_data = response.json()
    data = rest_data.get("data", [])

    table = Table(title="Clients", box=box.SIMPLE)
    table.add_column("No", justify="left", style="cyan")
    table.add_column("Name", justify="left")

    for i, item in enumerate(data):
        table.add_row(str(i + 1), item)

    cprint(table)


def add_client(**kwargs):
    """add client"""

    cprint("\nSave Client Facts", style="bold underline")

    response = api_client.post("/api/v1/registry/clients", json=kwargs)
    rest_data = response.json()
    data = rest_data.get("data", {})

    cprint(data)


def update_client(**kwargs):
    """add/update client"""
    client = kwargs.pop(P_CLIENT, None)
    if not client:
        raise ValueError("Client name is required")

    cprint("\nSave Client Facts", style="bold underline")

    data = {k: v for k, v in kwargs.items() if v is not None}

    request = api_client.put(f"/api/v1/registry/client/{client}", json=data)
    rest_data = request.json()
    data = rest_data.get("data", {})

    cprint(data)


def delete_client(**kwargs):
    """delete client"""
    client = kwargs.pop(P_CLIENT, None)
    if not client:
        raise ValueError("Client name is required")

    cprint("\nSaving client facts to the database...")

    response = api_client.delete(f"/api/v1/registry/client/{client}")
    rest_data = response.json()
    data = rest_data.get("data", {})

    cprint(data)


def get_client(**kwargs):
    """get client"""
    client = kwargs.pop(P_CLIENT, None)
    if not client:
        raise ValueError("Client name is required")

    cprint("\nGetting Client Facts\n", style="bold underline")

    response = api_client.get(f"/api/v1/registry/client/{client}")
    rest_data = response.json()
    data = rest_data.get("data", {})

    table = Table(title="Client Facts", box=box.SIMPLE)
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Value", justify="left", style="magenta")

    for k, v in data.items():
        table.add_row(k, v)

    cprint(table)


TASKS: ExecuteCommandsType = {
    "list": ("List all clients/organizations", list_clients),
    "get": ("Get client/organization", get_client),
    "add": ("Add new client/organization", add_client),
    "update": ("Update client/organization", update_client),
    "delete": ("Delete client/organization", delete_client),
}


def add_arguments(parser):
    """Add the clients arguments"""
    parser.add_argument(
        "--client",
        dest=P_CLIENT,
        metavar="<name>",
        help="Client alias name of the organization",
        required=False,
    )
    parser.add_argument(
        "--client-region",
        dest=P_CLIENT_REGION,
        metavar="<region>",
        help="Client region",
        required=False,
    )
    parser.add_argument(
        "--org-id",
        dest=P_ORGANIZATION_ID,
        metavar="<id>",
        help="Organization ID",
        required=False,
    )
    parser.add_argument(
        "--org-name",
        dest=P_ORGANIZATION_NAME,
        metavar="<name>",
        help="Organization name",
        required=False,
    )
    parser.add_argument(
        "--org-account",
        dest=P_ORGANIZATION_ACCOUNT,
        metavar="<account>",
        help="Organization AWS Account ID",
        required=False,
    )
    parser.add_argument(
        "--org-email",
        dest=P_ORGANIZATION_EMAIL,
        metavar="<emauk>",
        help="Organization email address",
        required=False,
    )
    parser.add_argument(
        "--automation-account",
        dest=P_AUTOMATION_ACCOUNT,
        metavar="<account>",
        help="Automaton AWS Account ID",
        required=False,
    )
    parser.add_argument(
        "--region",
        dest=P_REGION,
        metavar="<region>",
        help="AWS region for the master Automation account",
        required=False,
    )


def get_clients_command(subparsers) -> ExecuteCommandsType:
    """add the portfolios parser"""

    description = "Manage clients (a.k.a AWS Organizations)"

    subparser = subparsers.add_parser(
        "clients",
        description=description,
        choices=TASKS,
        help=description,
    )

    subparser.set_group_title(0, "Available Clients actions")
    subparser.set_group_title(1, "Available Clients options")

    add_arguments(subparser)

    subparser.add_argument("action", choices=TASKS.keys(), help="The action to perform")

    return {"clients": (description, execute_clients)}


def execute_clients(**kwargs):
    """Execute the clients command"""
    action = kwargs.get("action", None)
    if action in TASKS:
        TASKS[action][1](**kwargs)
