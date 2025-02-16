"""Client management module for core CLI.

Provides commands and utilities for managing AWS organization clients through the CLI,
including listing, adding, updating, and deleting client information.
"""

from rich.table import Table
from rich import box

from core_framework.constants import (
    P_SCOPE,
    P_CLIENT,
    P_CLIENT_NAME,
    P_CLIENT_REGION,
    P_ORGANIZATION_ID,
    P_ORGANIZATION_NAME,
    P_ORGANIZATION_ACCOUNT,
    P_ORGANIZATION_EMAIL,
    P_AUTOMATION_ACCOUNT,
    P_REGION,
    P_MASTER_REGION,
    P_SECURITY_ACCOUNT,
    P_AUDIT_ACCOUNT,
    P_NETWORK_ACCOUNT,
    P_DOMAIN,
    P_BUCKET_REGION,
    P_BUCKET_NAME,
    P_ARTEFACT_BUCKET_NAME,
    P_DOCUMENT_BUCKET_NAME,
    P_UI_BUCKET_NAME,
)
import core_framework as util

from core_cli.console import cprint
from core_cli.cmdparser import ExecuteCommandsType
from core_cli.apiclient import APIClient


def show_client(data):

    table = Table(title="Client Facts", box=box.SIMPLE)
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Value", justify="left", style="magenta")

    for k, v in data.items():
        table.add_row(k, v)

    cprint(table)


def list_clients(**kwargs):
    """list clients"""

    cprint("\nList Clients\n", style="bold underline")

    apiclient = APIClient.get_instance()
    headers = apiclient.get_headers(kwargs)

    response = apiclient.get("/api/v1/registry/clients", headers=headers)
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

    client = kwargs.get(P_CLIENT, None)
    if not client:
        raise ValueError("Client name is required")

    # The json serializer in api_client.post() does not handle datetime or some other types properly
    data = {
        P_SCOPE: kwargs.get(P_SCOPE) or util.get_automation_scope(),
        P_CLIENT: kwargs.get(P_CLIENT) or util.get_client(),
        P_CLIENT_NAME: kwargs.get(P_CLIENT_NAME) or util.get_client_name(),
        P_CLIENT_REGION: kwargs.get(P_CLIENT_REGION) or util.get_client_region(),
        P_MASTER_REGION: kwargs.get(P_MASTER_REGION) or util.get_region(),
        P_ORGANIZATION_ID: kwargs.get(P_ORGANIZATION_ID) or util.get_organization_id(),
        P_ORGANIZATION_NAME: kwargs.get(P_ORGANIZATION_NAME)
        or util.get_organization_name(),
        P_ORGANIZATION_ACCOUNT: kwargs.get(P_ORGANIZATION_ACCOUNT)
        or util.get_organization_account()
        or util.get_automation_account(),
        P_ORGANIZATION_EMAIL: kwargs.get(P_ORGANIZATION_EMAIL)
        or util.get_organization_email(),
        P_AUTOMATION_ACCOUNT: kwargs.get(P_AUTOMATION_ACCOUNT)
        or util.get_automation_account(),
        P_SECURITY_ACCOUNT: kwargs.get(P_SECURITY_ACCOUNT)
        or util.get_security_account()
        or util.get_automation_account(),
        P_AUDIT_ACCOUNT: kwargs.get(P_AUDIT_ACCOUNT)
        or util.get_audit_account()
        or util.get_automation_account(),
        P_NETWORK_ACCOUNT: kwargs.get(P_NETWORK_ACCOUNT)
        or util.get_network_account()
        or util.get_automation_account(),
        P_DOMAIN: kwargs.get(P_DOMAIN) or (util.get_domain()),
        P_BUCKET_REGION: kwargs.get(P_BUCKET_REGION) or util.get_bucket_region(),
        P_BUCKET_NAME: kwargs.get(P_BUCKET_NAME) or util.get_bucket_name(client),
        P_ARTEFACT_BUCKET_NAME: kwargs.get(P_ARTEFACT_BUCKET_NAME)
        or util.get_artefact_bucket_name(client),
        P_DOCUMENT_BUCKET_NAME: kwargs.get(P_DOCUMENT_BUCKET_NAME)
        or util.get_document_bucket_name(client),
        P_UI_BUCKET_NAME: kwargs.get(P_UI_BUCKET_NAME)
        or util.get_ui_bucket_name(client),
    }

    apiclient = APIClient.get_instance()
    headers = apiclient.get_headers(kwargs)
    response = apiclient.post("/api/v1/registry/clients", headers=headers, json=data)
    rest_data = response.json()
    data = rest_data.get("data", {})

    show_client(data)


def update_client(**kwargs):
    """add/update client"""
    client = kwargs.pop(P_CLIENT, None)
    if not client:
        raise ValueError("Client name is required")

    cprint("\nSave Client Facts", style="bold underline")

    keys = [
        P_SCOPE,
        P_CLIENT,
        P_CLIENT_NAME,
        P_CLIENT_REGION,
        P_MASTER_REGION,
        P_ORGANIZATION_ID,
        P_ORGANIZATION_NAME,
        P_ORGANIZATION_ACCOUNT,
        P_ORGANIZATION_EMAIL,
        P_AUTOMATION_ACCOUNT,
        P_SECURITY_ACCOUNT,
        P_AUDIT_ACCOUNT,
        P_NETWORK_ACCOUNT,
        P_DOMAIN,
        P_BUCKET_REGION,
        P_BUCKET_NAME,
        P_ARTEFACT_BUCKET_NAME,
        P_DOCUMENT_BUCKET_NAME,
        P_UI_BUCKET_NAME,
    ]

    data = {
        key: kwargs[key] for key in keys if key in kwargs and kwargs[key] is not None
    }

    apiclient = APIClient.get_instance()
    headers = apiclient.get_headers(kwargs)
    request = apiclient.patch(
        f"/api/v1/registry/client/{client}", headers=headers, json=data
    )
    rest_data = request.json()
    data = rest_data.get("data", {})

    show_client(data)


def delete_client(**kwargs):
    """delete client"""
    client = kwargs.pop(P_CLIENT, None)
    if not client:
        raise ValueError("Client name is required")

    cprint("\nSaving client facts to the database...")

    apiclient = APIClient.get_instance()
    headers = apiclient.get_headers(kwargs)

    response = apiclient.delete(f"/api/v1/registry/client/{client}", headers=headers)
    rest_data = response.json()
    data = rest_data.get("data", {})

    cprint(data)


def get_client(**kwargs):
    """get client"""
    client = kwargs.pop(P_CLIENT, None)
    if not client:
        raise ValueError("Client name is required")

    cprint("\nGetting Client Facts\n", style="bold underline")

    apiclient = APIClient.get_instance()
    headers = apiclient.get_headers(kwargs)

    response = apiclient.get(f"/api/v1/registry/client/{client}", headers=headers)
    rest_data = response.json()
    data = rest_data.get("data", {})

    show_client(data)


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
        "--scope",
        dest=P_SCOPE,
        metavar="<scope>",
        help="Automation Engine scope",
        required=False,
    )
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
        "--client-name",
        dest=P_CLIENT_NAME,
        metavar="<name>",
        help="Client name",
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
    parser.add_argument(
        "--security-account",
        dest=P_SECURITY_ACCOUNT,
        metavar="<account>",
        help="Security AWS Account ID",
        required=False,
    )
    parser.add_argument(
        "--audit-account",
        dest=P_AUDIT_ACCOUNT,
        metavar="<account>",
        help="Audit AWS Account ID",
        required=False,
    )
    parser.add_argument(
        "--network-account",
        dest=P_NETWORK_ACCOUNT,
        metavar="<account>",
        help="Network AWS Account ID",
        required=False,
    )
    parser.add_argument(
        "--domain",
        dest=P_DOMAIN,
        metavar="<domain>",
        help="Top level Domain name of the organization (e.g. example.com)",
        required=False,
    )
    parser.add_argument(
        "--bucket-region",
        dest=P_BUCKET_REGION,
        metavar="<region>",
        help="AWS region for the bucket to contain the pacakge details (e.g. us-west-2)",
        required=False,
    )
    parser.add_argument(
        "--bucket-name",
        dest=P_BUCKET_NAME,
        metavar="<name>",
        help="Bucket name for the package details (e.g. my-sws-cdk-bucket)",
        required=False,
    )
    parser.add_argument(
        "--artefact-bucket-name",
        dest=P_ARTEFACT_BUCKET_NAME,
        metavar="<name>",
        help="Bucket name for the artefacts (e.g. my-sws-cdk-bucket)",
        required=False,
    )
    parser.add_argument(
        "--document-bucket-name",
        dest=P_DOCUMENT_BUCKET_NAME,
        metavar="<name>",
        help="Bucket name for the documents (e.g. my-docs-bucket)",
        required=False,
    )
    parser.add_argument(
        "--ui-bucket-name",
        dest=P_UI_BUCKET_NAME,
        metavar="<name>",
        help="Bucket name for the UI files (e.g. my-ui-bucket)",
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
