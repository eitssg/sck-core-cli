from ...cmdparser import ExecuteCommandsType


def list_apps(**kwargs):
    """list apps"""
    print(kwargs)

    print("List Apps")

    # response = PortfolioActions.list(items="all")
    # data = response.get("Items", [])

    # table = Table(title="Portfolios", box=box.SIMPLE)
    # table.add_column("Name", justify="left", style="cyan")

    # for item in data:
    #     table.add_row(item["name"])

    # cprint(table)


def add_app(**kwargs):
    """add app"""
    print(kwargs)
    print("Add App")


def update_app(**kwargs):
    """add/update app"""
    print(kwargs)
    print("Add/Update App")


def delete_app(**kwargs):
    """delete app"""
    print(kwargs)
    print("Delete App")


TASKS: ExecuteCommandsType = {
    "list": ("List all apps/deployments", list_apps),
    "add": ("Add new app/deployment", add_app),
    "update": ("Update app/deployment", update_app),
    "delete": ("Delete app/deployment", delete_app),
}


def get_apps_command(subparsers) -> ExecuteCommandsType:
    """add the apps parser"""

    description = "Manage apps (a.k.a Deployments or CloudFormation Stack)"

    subparser = subparsers.add_parser(
        "apps",
        description=description,
        help=description,
    )

    subparser.set_group_title(0, "Available Apps actions")
    subparser.set_group_title(1, "Available Apps options")

    return {"apps": (description, execute_apps)}


def execute_apps(**kwargs):
    """Execute the apps command"""
    action = kwargs.get("action", None)
    if action in TASKS:
        TASKS[action][1](**kwargs)
