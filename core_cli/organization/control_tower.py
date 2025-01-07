"""Show control-tower stuff"""

from rich.console import Console
from rich.table import Table
from rich import box

from ..cmdparser import ExecuteCommandsType

from .common import exexecution_check, cprint

console = Console()


def describe_control_tower(**kwargs):
    """Describe the status of AWS Control Tower in the organization."""

    exexecution_check(kwargs)

    cprint(
        """
Please note that as of now this function peforms no task

It is a placeholder for future development.

You [bold]DO NOT NEED[bold] to enable Control Tower with core-automation.  It is NOT a
a prerequisite for using core-automation.  You can use core-automation deployment
lifecycles without Control Tower.  You can even manage "Landing Zones" wihtout Control Tower.

If you wish to use Contol Tower to provision a Landing Zone, you can do so.  And you can
use the account-factory with Control Tower instead of Core-Automation "Account-Setup"

The core-automation tools will help you setup Account Factory.  If you really want to.

Please be aware of the following information before you begin using Control Tower
Landing Zone provisioning:
    """
    )

    table = Table(box=box.SQUARE)
    table.add_column("Control Tower")
    table.add_column("Description")
    table.add_column("Comment")

    table.add_row(
        "Simple Storage Service (Amazon S3)",
        "Stores all logs and artifacts",
        "$$ Please note that this service is used heavily.  You can expect more than $500/month on S3 using landing zones",
    )
    table.add_row(
        "AWS Config",
        "Stores all configuration information",
        "$$$$$ This service is used for Security Hub and compliance checks.  You can expect more than $1000/month on AWS Config when it is enabled for a typical workloads.  If yo have highly elastic workloads, this can go up to $5000/month",
    )
    table.add_row(
        "AWS CloudTrail",
        "Stores all API calls",
        "$$ This service is used for security and compliance checks.  You can expect more than $500/month on CloudTrail when it is enabled for a typical workloads.  You will pay VPC Egress Fees and S3 storage costs of more than $500/month",
    )
    table.add_row(
        "Amazon SNS",
        "Internal communications between services",
        "$ This service is used for notifications.  You can expect more than $100/month on SNS when it is enabled for a typical workloads.  Cost is minimal",
    )
    table.add_row(
        "Virgual Private Cloud",
        "Network isolation",
        "$$# This service is used for network isolation with Control-Twower landing zones.  You cannot have more than one zone per VPC. Expected $200/month on VPC data egress fees for CloudTrail and VPC flow logs (You MUST ensure Endpoint services are enabled tp prevent $$$$ Thousands in data flow costs)",
    )
    table.add_row(
        "AWS Lambda",
        "Serverless computing",
        "$ This service is used for automation.  You can expect more than $100/month on Lambda when it is enabled for a typical workloads.  Cost is minimal",
    )
    table.add_row(
        "CloudFormation",
        "Infrastructure as Code",
        '$ This service is used for automation.  You can expect more than $1000/month on CloudFormation.  It calls API.  It is easy to go over the "free-tier" and API costs explode',
    )
    table.add_row(
        "Amazon CloudWatch",
        "Monitoring and logging",
        "$$$$ This service is used for monitoring and logging.  You can expect more than $300/month on CloudWatch when it is enabled for a typical workloads.",
    )
    table.add_row(
        "AWS Identity and Access Management (IAM)",
        "Security and access control",
        "$ This service is used for security and access control.  You can expect more than $100/month on IAM when it is enabled for a typical workloads.  Cost is minimal",
    )

    cprint(table)

    cprint(
        "\nPlease note that running an typical workload in an AWS Control Tower managed landing zone can easily exceed "
        "$1500/month in the workload accounts and more than $1000/month per workload deployment in the management and "
        "shared services acocunts\n\n"
    )

    cprint(
        "Please expect that with Control Tower, your baseline operation cosst in AWS will be between $2500 and $10000/month\n\n"
    )


def get_control_tower_tasks(parser) -> ExecuteCommandsType:
    """Get the parser for the control tower command."""
    control_tower_parser = parser.add_parser(
        "ct",
        help="Control Tower operations",
        description="Control Tower operations",
    )

    control_tower_parser.add_argument(
        "task",
        choices=["describe"],
        metavar="<task>",
        help="Command:\n\ndescribe : Describe the status of AWS Control Tower in the organization.",
    )

    return {"ct": ("Control Tower Operations", execute_control_tower)}


def execute_control_tower(**kwargs):
    """Execute the control tower task."""

    task = kwargs.get("task")
    if task == "describe":
        describe_control_tower(**kwargs)
    else:
        console.print("Unknown task", style="bold red")
