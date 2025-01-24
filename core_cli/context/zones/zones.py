from ...cmdparser import ExecuteCommandsType


def list_zones(**kwargs):
    """list zones"""
    print(kwargs)

    print("List Zones")

    # response = PortfolioActions.list(items="all")
    # data = response.get("Items", [])

    # table = Table(title="Portfolios", box=box.SIMPLE)
    # table.add_column("Name", justify="left", style="cyan")

    # for item in data:
    #     table.add_row(item["name"])

    # cprint(table)


def add_zone(**kwargs):
    """add zone"""
    print(kwargs)
    print("Add Zone")


def update_zone(**kwargs):
    """add/update zone"""
    print(kwargs)
    print("Add/Update Zone")


def delete_zone(**kwargs):
    """delete zone"""
    print(kwargs)
    print("Delete Zone")


TASKS: ExecuteCommandsType = {
    "list": ("List all zones", list_zones),
    "add": ("Add new zone", add_zone),
    "update": ("Update zone", update_zone),
    "delete": ("Delete zone", delete_zone),
}


def execute_zones(**kwargs):
    """Execute the portfolio command"""
    action = kwargs.get("action", None)
    if action in TASKS:
        TASKS[action][1](**kwargs)


def get_zones_command(subparsers) -> ExecuteCommandsType:
    """add the zones parser"""

    description = "Manage zones Facts (AWS Accounts and Regions)"

    subparser = subparsers.add_parser(
        "zones",
        description=description,
        choices=TASKS,
        help=description,
    )

    subparser.set_group_title(0, "Avalable actions")
    subparser.set_group_title(1, "Available options")

    subparser.add_argument("action", choices=TASKS.keys(), help="The action to perform")

    return {"zones": (description, execute_zones)}
