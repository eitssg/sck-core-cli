from rich.table import Table
from rich import box

import core_helper.aws as aws

from core_cli.common import cprint
from core_cli.cmdparser import ExecuteCommandsType


def list_domains(**kwargs):
    # Create a Route 53 client
    client = aws.r53_client()

    try:
        # Call the list_domains method to retrieve all registered domains
        response = client.list_hosted_zones()

        # Extract the domains from the response
        domains = [zone['Name'] for zone in response['HostedZones']]

        table = Table(box=box.SIMPLE)
        table.add_column("DomainName", justify="left")

        # Print the domains
        for domain in domains:
            table.add_row(domain)

        cprint(table)

    except Exception as e:
        cprint(f"An error occurred: {e}", style="red")


DOMAIN_TASKS: ExecuteCommandsType = {
    "list": ("List the domains in the organization", list_domains)
}


def get_domain_command(subparsers) -> ExecuteCommandsType:
    """Get the parser for the configuration command"""

    description = "Manage the domains in the organization"

    domain_parser = subparsers.add_parser(
        "domains",
        description=description,
        usage="core domains [<task>] [--client <name>]",
        choices=DOMAIN_TASKS,
        help=description,
    )
    domain_parser.set_group_title(0, "Configure actions")
    domain_parser.set_group_title(1, "Available options")

    domain_parser.add_argument(
        "task",
        choices=DOMAIN_TASKS.keys(),
        help="List all the domains in the organization",
    )

    return {"domains": (description, execute_domains)}


def execute_domains(**kwargs):
    """Configure the client vars for the specified client."""
    task = kwargs.get("task")
    if task in DOMAIN_TASKS:
        DOMAIN_TASKS[task][1](**kwargs)
