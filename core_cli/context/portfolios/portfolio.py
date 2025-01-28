from rich.table import Table
from rich import box

from core_framework.constants import P_CLIENT, P_PORTFOLIO, P_PROJECT, P_DOMAIN, P_BIZAPP

from core_db.registry import PortfolioActions

from core_cli.common import cprint
from core_cli.cmdparser import ExecuteCommandsType


def list_portfolios(**kwargs):
    """list portfolios"""
    print(kwargs)

    print("List Portfolios")

    response = PortfolioActions.list(items="all")
    data = response.get("Items", [])

    table = Table(title="Portfolios", box=box.SIMPLE)
    table.add_column("Name", justify="left", style="cyan")

    for item in data:
        table.add_row(item["name"])

    cprint(table)


def add_portfolio(**kwargs):
    """add portfolio"""
    print(kwargs)
    print("Add Portfolio")

    data = {
        P_CLIENT: "myorg",
        P_PORTFOLIO: "myportfolio",
        P_PROJECT: "myproject",
        P_DOMAIN: "mydomain",
        P_BIZAPP: "mybizapp",
    }





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

    subparser.add_argument(
        "-p", "--portfolio", help="Specifiy one portfolio by name")

    return {"portfolios": (description, execute_portfolio)}
