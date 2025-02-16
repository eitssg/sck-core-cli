from rich.table import Table
from rich import box

import core_framework as util
from core_framework.constants import (
    P_CLIENT,
    P_PORTFOLIO,
    P_PROJECT,
    P_DOMAIN,
    P_BIZAPP,
)

from core_cli.console import cprint, jprint
from core_cli.cmdparser import ExecuteCommandsType
from core_cli.apiclient import APIClient


def list_portfolios(**kwargs):
    """list portfolios"""
    print(kwargs)

    print("List Portfolios")

    api_client = APIClient.get_instance()
    headers = api_client.get_headers(kwargs)

    response = api_client.get("/api/v1/portfolios", headers=headers)
    json_data = response.json()
    data = json_data.get("data", [])

    table = Table(title="Portfolios", box=box.SIMPLE)
    table.add_column("Name", justify="left", style="cyan")

    for item in data:
        table.add_row(item["name"])

    cprint(table)


def add_portfolio(**kwargs):
    """add portfolio"""
    jprint(util.to_json(kwargs))

    cprint("Add Portfolio", style="bold underline")

    data = {
        P_CLIENT: kwargs.get(P_CLIENT, util.get_client()),
        P_PORTFOLIO: kwargs.get(P_PORTFOLIO, None),
        P_PROJECT: kwargs.get(P_PROJECT, None),
        P_DOMAIN: kwargs.get(P_DOMAIN, None),
        P_BIZAPP: kwargs.get(P_BIZAPP, kwargs.get(P_PORTFOLIO, None)),
    }

    api_client = APIClient.get_instance()
    headers = api_client.get_headers(kwargs)

    response = api_client.post("/api/v1/portfolios", json=data, headers=headers)
    json_data = response.json()
    data = json_data.get("data", [])

    cprint(data)


def update_portfolio(**kwargs):
    """add/update portfolio"""
    print(kwargs)
    print("Add/Update Portfolio")


def delete_portfolio(**kwargs):
    """delete portfolio"""
    print(kwargs)
    print("Delete Portfolio")


TASKS: ExecuteCommandsType = {
    "list": ("List all portfolios", list_portfolios),
    "add": ("Add new portfolio", add_portfolio),
    "update": ("Update portfolio", update_portfolio),
    "delete": ("Delete portfolio", delete_portfolio),
}


def execute_portfolio(**kwargs):
    """Execute the portfolio command"""
    action = kwargs.get("action", None)
    if action in TASKS:
        TASKS[action][1](**kwargs)


def get_portfolios_command(subparsers) -> ExecuteCommandsType:
    """add the portfolio parser"""

    description = "Manage portfolios (a.k.a Business Applications or AWS StackSets)"

    subparser = subparsers.add_parser(
        "portfolios",
        description=description,
        choices=TASKS,
        help=description,
    )

    subparser.set_group_title(0, "Avalable actions")
    subparser.set_group_title(1, "Available options")

    subparser.add_argument("action", choices=TASKS.keys(), help="The action to perform")

    subparser.add_argument("-p", "--portfolio", help="Specifiy one portfolio by name")

    return {"portfolios": (description, execute_portfolio)}
