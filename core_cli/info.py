from rich.table import Table
from rich import box

import core_framework as util
from core_framework.constants import (
    P_USERNAME,
    P_AWS_PROFILE,
    P_CLIENT,
    P_PORTFOLIO,
    P_APP,
    P_BRANCH,
    P_ENVIRONMENT,
    P_BUILD,
    P_REGION,
    P_CLIENT_REGION,
    P_SCOPE,
    P_AUTOMATION_ACCOUNT,
    P_ITEMS_TABLE_NAME,
    P_EVENTS_TABLE_NAME,
    P_CLIENT_TABLE_NAME,
    P_PORTFOLIOS_TABLE_NAME,
    P_ZONES_TABLE_NAME,
    P_APPS_TABLE_NAME,
    P_BUCKET_REGION,
    P_BUCKET_NAME,
    P_ARTEFACT_BUCKET_NAME,
    P_DYNAMODB_HOST,
    P_DYNAMODB_REGION,
    P_USE_S3,
    P_ORGANIZATION_ID,
    P_ORGANIZATION_ACCOUNT,
    P_ORGANIZATION_NAME,
    P_ORGANIZATION_EMAIL,
    ENV_SCOPE,
    ENV_CLIENT,
    ENV_CLIENT_NAME,
    ENV_CLIENT_REGION,
    ENV_AWS_PROFILE,
    ENV_AUTOMATION_ACCOUNT,
    ENV_AWS_REGION,
    ENV_DYNAMODB_HOST,
    ENV_DYNAMODB_REGION,
    ENV_BUCKET_REGION,
    ENV_BUCKET_NAME,
    ENV_ARTEFACT_BUCKET_NAME,
)

from core_db.config import get_table_name
from core_db.constants import (
    ITEMS,
    EVENTS,
    CLIENT_FACTS,
    PORTFOLIO_FACTS,
    ZONE_FACTS,
    APP_FACTS,
)

from core_cli import __version__

from .console import cprint, get_organization_info
from .cmdparser import ExecuteCommandsType
from .environment import print_environmnt

APP = "cli"
PORTFOLIO = "core"
BRANCH = "main"
ENVIRONMENT = "prod"


def show_configuration(data):

    username = data[P_USERNAME]
    aws_profile = data[P_AWS_PROFILE]
    client = data[P_CLIENT]

    data[P_PORTFOLIO] = PORTFOLIO
    data[P_APP] = APP
    data[P_BRANCH] = BRANCH
    data[P_ENVIRONMENT] = ENVIRONMENT
    data[P_BUILD] = __version__

    data[P_REGION] = region = util.get_region()
    data[P_CLIENT_REGION] = client_region = util.get_client_region()

    data[P_SCOPE] = scope_prefix = util.get_automation_scope() or ""
    data[P_AUTOMATION_ACCOUNT] = automation_account = util.get_automation_account()

    data[P_ITEMS_TABLE_NAME] = items_table_name = get_table_name(ITEMS)
    data[P_EVENTS_TABLE_NAME] = events_table_name = get_table_name(EVENTS)
    data[P_CLIENT_TABLE_NAME] = clients_table = get_table_name(CLIENT_FACTS)
    data[P_PORTFOLIOS_TABLE_NAME] = portfolios_table = get_table_name(PORTFOLIO_FACTS)
    data[P_ZONES_TABLE_NAME] = zones_table = get_table_name(ZONE_FACTS)
    data[P_APPS_TABLE_NAME] = apps_table = get_table_name(APP_FACTS)

    data[P_BUCKET_REGION] = bucket_region = util.get_bucket_region()
    data[P_BUCKET_NAME] = automation_bucket = util.get_bucket_name(client)
    data[P_ARTEFACT_BUCKET_NAME] = artefacts_bucket = util.get_artefact_bucket_name(
        client
    )
    data[P_DYNAMODB_HOST] = dynamodb_host = util.get_dynamodb_host()
    data[P_DYNAMODB_REGION] = dynamodb_region = util.get_dynamodb_region()
    data[P_USE_S3] = util.is_use_s3()

    if P_ORGANIZATION_ID not in data:
        org = get_organization_info()
        data[P_ORGANIZATION_ID] = org["Id"]
        data[P_ORGANIZATION_ACCOUNT] = org["AccountId"]
        data[P_ORGANIZATION_NAME] = org["Name"]
        data[P_ORGANIZATION_EMAIL] = org["Email"]

    orgnaniation_id = data[P_ORGANIZATION_ID]
    management_account = data[P_ORGANIZATION_ACCOUNT]
    organization_name = data[P_ORGANIZATION_NAME]
    organization_email = data[P_ORGANIZATION_EMAIL]

    table = Table(box=box.SIMPLE)
    table.add_column("Item", style="cyan")
    table.add_column("Current Value", style="dark_orange")
    table.add_column("Environment Variable", style="dark_goldenrod")

    table.add_row("Scope Prefix", scope_prefix, ENV_SCOPE)
    table.add_row("Organization Client", client, ENV_CLIENT)
    table.add_row("Organization Name", organization_name, ENV_CLIENT_NAME)
    table.add_row("Organization Email", organization_email, "")
    table.add_row("Organization ID", orgnaniation_id, "")
    table.add_row("Client Region", client_region, ENV_CLIENT_REGION)
    table.add_row("Management Account", management_account, "")
    table.add_row("AWS Profile", aws_profile, ENV_AWS_PROFILE)
    table.add_row("Administrator Username", username, "")
    table.add_row("Automation Account", automation_account, ENV_AUTOMATION_ACCOUNT)
    table.add_row("Automation Region", region, ENV_AWS_REGION)
    table.add_row("Dynamodb Host", dynamodb_host, ENV_DYNAMODB_HOST)
    table.add_row("Dynamedb Region", dynamodb_region, ENV_DYNAMODB_REGION)
    table.add_row("Deployment Items Table", items_table_name, "")
    table.add_row("Deployment Events Table", events_table_name, "")
    table.add_row("Client Facts Table", clients_table, "")
    table.add_row("Portfolio Facts Table", portfolios_table, "")
    table.add_row("Zone Facts Table", zones_table, "")
    table.add_row("App Facts Table", apps_table, "")
    table.add_row("Bucket Region", bucket_region, ENV_BUCKET_REGION)
    table.add_row("Automation Bucket", automation_bucket, ENV_BUCKET_NAME)
    table.add_row("Artefacts Bucket", artefacts_bucket, ENV_ARTEFACT_BUCKET_NAME)
    table.add_row("User Role", f"{scope_prefix}CoreAutomationApiRead", "")
    table.add_row("Api Admin Role", f"{scope_prefix}CoreAutomationApiWrite", "")
    table.add_row("Core Admin Role", f"{scope_prefix}CorePipelineProvisioning", "")
    table.add_row("Core Control Role", f"{scope_prefix}CorePipelineControl", "")

    cprint(table)

    print_environmnt()


def execute_info(**kwargs):

    cprint(f"Core Automation Information v{__version__}\n")

    cprint("This is the core CLI information:\n")

    show_configuration(kwargs)


def get_info_command(subparsers) -> ExecuteCommandsType:

    DESCRIPTION = "Display information about the core subsystem"

    config_parser = subparsers.add_parser(
        "info", description=DESCRIPTION, usage="core info", help=DESCRIPTION
    )
    config_parser.set_group_title(0, "Configure actions")
    config_parser.set_group_title(1, "Available options")

    return {"info": (DESCRIPTION, execute_info)}
