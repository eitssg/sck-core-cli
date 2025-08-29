from typing import Callable
import core_db.config
from rich.table import Table
from rich import box
import subprocess
import os

from core_db.registry import ClientActions, ZoneActions, PortfolioActions, AppActions

import core_cli.resources
import core_db.platform
import core_framework as util
from core_framework.constants import (
    ENV_SCOPE,
    ENV_CLIENT,
    ENV_CLIENT_NAME,
    ENV_AWS_PROFILE,
    ENV_AWS_REGION,
    ENV_DYNAMODB_HOST,
    ENV_DYNAMODB_REGION,
    ENV_AUTOMATION_ACCOUNT,
    ENV_BUCKET_NAME,
    ENV_BUCKET_REGION,
    ENV_ARTEFACT_BUCKET_NAME,
    ENV_CLIENT_REGION,
    ENV_USE_S3,
    P_SCOPE,
    P_CLIENT,
    P_ORGANIZATION_ID,
    P_ORGANIZATION_ACCOUNT,
    P_ORGANIZATION_NAME,
    P_ORGANIZATION_EMAIL,
    P_AWS_PROFILE,
    P_USERNAME,
    P_CURRENT_ACCOUNT,
    P_AUTOMATION_ACCOUNT,
    P_IDENTITY,
    P_REGION,
    P_MASTER_REGION,
    P_BUCKET_NAME,
    P_BUCKET_REGION,
    P_ARTEFACT_BUCKET_NAME,
    P_CLIENT_REGION,
    P_CLIENT_TABLE_NAME,
    P_PORTFOLIOS_TABLE_NAME,
    P_ZONES_TABLE_NAME,
    P_APPS_TABLE_NAME,
    P_ITEMS_TABLE_NAME,
    P_EVENTS_TABLE_NAME,
    P_TEMPLATE,
    P_STACK_NAME,
    P_STACK_PARAMETERS,
    P_DYNAMODB_HOST,
    P_DYNAMODB_REGION,
    P_PORTFOLIO,
    P_APP,
    P_BRANCH,
    P_BUILD,
    P_ENVIRONMENT,
    P_USE_S3,
    P_TAGS,
    TAG_CLIENT,
    TAG_SCOPE,
    TAG_PORTFOLIO,
    TAG_APP,
    TAG_BRANCH,
    TAG_BUILD,
    TAG_ENVIRONMENT,
)

import core_db.registry

from core_cli import __version__

from ..info import show_configuration
from ..cmdparser import ExecuteCommandsType
from ..console import (
    get_input,
    cprint,
    get_iam_user_name,
    check_admin_privileges,
    get_organization_info,
)

from .deploy import start_deploy_stack

PORTFOLIO = "core"
BRANCH = "main"
ENVIRONMENT = "prod"
ZONE_REGION_KEY = "sin"


def get_tags(data: dict, app: str) -> dict:

    data[P_PORTFOLIO] = PORTFOLIO
    data[P_APP] = app
    data[P_BRANCH] = BRANCH
    data[P_BUILD] = __version__
    data[P_ENVIRONMENT] = ENVIRONMENT

    return {
        TAG_CLIENT: data[P_CLIENT],
        TAG_SCOPE: data[P_SCOPE],
        TAG_PORTFOLIO: data[P_PORTFOLIO],
        TAG_APP: data[P_APP],
        TAG_BRANCH: data[P_BRANCH],
        TAG_BUILD: data[P_BUILD],
        TAG_ENVIRONMENT: data[P_ENVIRONMENT],
    }


def deploy_roles(data, next) -> str:

    cprint("\nDEPLOY ROLES\n", style="bold underline")

    scope_prefix = data[P_SCOPE]
    clients_table_name = data[P_CLIENT_TABLE_NAME]
    zones_table_name = data[P_ZONES_TABLE_NAME]
    portfolios_table_name = data[P_PORTFOLIOS_TABLE_NAME]
    app_table_name = data[P_APPS_TABLE_NAME]
    bucket_name = data[P_BUCKET_NAME]
    artefact_bucket_name = data[P_ARTEFACT_BUCKET_NAME]

    cli_project_dir = os.path.dirname(os.path.realpath(core_cli.resources.__file__))

    tags = get_tags(data, "roles")

    data["parameters"] = {
        "ClientsTableName": clients_table_name,
        "ZonesTableName": zones_table_name,
        "PortfoliosTableName": portfolios_table_name,
        "AppsTableName": app_table_name,
        "BucketName": bucket_name,
        "ArtefactBucketName": artefact_bucket_name,
        **tags,
    }

    data[P_TEMPLATE] = os.path.join(cli_project_dir, "core-roles.yaml")
    data[P_STACK_NAME] = f"{scope_prefix}core-automation-roles"
    data[P_TAGS] = tags

    # Deploy the roles
    start_deploy_stack(**data)

    cprint("\nComplete!\n", style="bold green")

    result = get_input(
        "Press Enter to continue or X to abort.", ["Enter", "x"], "Enter"
    )
    if result.lower() == "x":
        raise Exception("Aborted by user.")

    return next


def deploy_storage(data, next) -> str:

    cprint("\nS3 BUCKET DEPLOYMENT\n", style="bold underline")

    client = data[P_CLIENT]
    organization_id = data[P_ORGANIZATION_ID]
    automation_account = data[P_AUTOMATION_ACCOUNT]
    scope_prefix = data[P_SCOPE]

    # bucket name should be; "${ScopePrefix}${Client}-core-automation-${AWS::Region}"
    automation_bucket = data[P_BUCKET_NAME]
    bucket_region = data[P_BUCKET_REGION]

    # bucket name should be; "${ScopePrefix}${Client}-core-automation-artefacts-${AWS::Region}"
    artefacts_bucket = data[P_ARTEFACT_BUCKET_NAME]

    # Update Client Vars with storage information
    ClientActions.patch(
        **{
            P_CLIENT: client,
            P_AUTOMATION_ACCOUNT: automation_account,
            P_BUCKET_NAME: automation_bucket,
            P_BUCKET_REGION: bucket_region,
            P_ARTEFACT_BUCKET_NAME: artefacts_bucket,
        }
    )

    cli_project_dir = os.path.dirname(os.path.realpath(core_cli.resources.__file__))

    tags = get_tags(data, "storage")

    data[P_STACK_PARAMETERS] = {
        "OrganizationId": organization_id,
        "AutomationBucketName": automation_bucket,
        "ArtefactsBucketName": artefacts_bucket,
        **tags,
    }

    data[P_TEMPLATE] = os.path.join(cli_project_dir, "core-storage.yaml")
    data[P_STACK_NAME] = f"{scope_prefix}core-automation-storage"
    data[P_TAGS] = tags

    # save the master region
    region = data[P_REGION]

    # Deploy the stack in the bucket region
    data[P_REGION] = bucket_region
    start_deploy_stack(**data)

    # Reset the master region
    data[P_REGION] = region

    cprint("\nComplete!\n", style="bold green")

    result = get_input(
        "Press Enter to continue or X to abort.", ["Enter", "x"], "Enter"
    )
    if result.lower() == "x":
        raise Exception("Aborted by user.")

    return next


def pre_storage(data, next) -> str:

    cprint("\nDEPLOY STORAGE\n", style="bold underline")

    cprint(
        "The next step will be installing the core automation storage.  Please read this note about storage.\n"
    )

    cprint(
        "The core automation storage is one or two S3 buckets that are used to store the core automation packages and\n"
        'artifacts.  The "packages" bucket is used to store files, code archives, and CloudFormation templates\n'
        '[yellow]prior[/yellow] to deployment.  The "artifacts" bucket is used to store [yellow]deployment[/yellow] artifacts, such as compiled,\n'
        "generated and transformed CloudFormation templates, deployment files, and other user defined content.\n"
    )

    cprint(
        'The "packages" and the "artefacts" bucket can be the same S3 bucket.  If you make them different, you\n'
        "will have the opportunity to have different security access configurations for each.\n"
    )

    cprint(
        "If you wish to deploy the lambda functions and run automation within AWS lambda, you must deploy the\n"
        "storage in S3.  If you do not deploy the storage, lambda function deployment will not be automated for you.\n"
    )

    cprint(
        "If you wish to only use the core automation docker container, you may skip this step.  Or, you can use S3\n"
        'if you wish. There is an environment variable for the docker container "USE_S3=true" that will\n'
        "enable the use of the S3 storage in docker.  Else, you will need to have a docker shared storage solution\n"
        'and use the environment variable [green]"VOLUME=N:\\data"[/green] or [green]"VOLUME=/mnt/data"[/green] as define in your docker iamage\n'
        "deployment.\n"
    )

    cprint("The following illustrates what will be installed:")

    automation_account = data[P_AUTOMATION_ACCOUNT]
    automation_bucket = data[P_BUCKET_NAME]
    automation_bucket_region = data[P_BUCKET_REGION]
    artefacts_bucket = data[P_ARTEFACT_BUCKET_NAME]
    use_s3 = data[P_USE_S3]

    table = Table(box=box.SIMPLE)
    table.add_column("Item", style="cyan")
    table.add_column("Description", style="dark_orange")
    table.add_column("Environment Variable", style="dark_goldenrod")

    table.add_row("Automation Account", automation_account, ENV_AUTOMATION_ACCOUNT)
    table.add_row("Bucket Region", automation_bucket_region, ENV_BUCKET_REGION)
    table.add_row("Packages Bucket", automation_bucket, ENV_BUCKET_NAME)
    table.add_row("Artifacts Bucket", artefacts_bucket, ENV_ARTEFACT_BUCKET_NAME)
    table.add_row("Use S3", str(use_s3), ENV_USE_S3)

    cprint(table)

    cprint(
        "If you wish to change any of the above values, please set the appropriate environment variables and restart setup.\n"
    )

    result = get_input(
        "Press Enter to continue, S to skip, or X to abort.",
        ["Enter", "x", "s"],
        "Enter",
    )
    if result.lower() == "x":
        raise Exception("Aborted by user.")
    if result.lower() == "s":
        return "done"

    return next


def register_client(data):

    client = data[P_CLIENT]

    cprint("\nSaving client facts to the database...")

    response = ClientActions.get(client=client)
    client_facts = response.data if isinstance(response.data, dict) else {}

    client_facts.update(
        {
            P_CLIENT: client,
            P_SCOPE: data[P_SCOPE],
            P_CLIENT_REGION: data[P_CLIENT_REGION],
            P_ORGANIZATION_ID: data[P_ORGANIZATION_ID],
            P_ORGANIZATION_NAME: data[P_ORGANIZATION_NAME],
            P_ORGANIZATION_ACCOUNT: data[P_ORGANIZATION_ACCOUNT],
            P_ORGANIZATION_EMAIL: data[P_ORGANIZATION_EMAIL],
            P_AUTOMATION_ACCOUNT: data[P_AUTOMATION_ACCOUNT],
            P_MASTER_REGION: data[P_REGION],
        }
    )

    ClientActions.update(**client_facts)


def register_zone(data):
    client = data[P_CLIENT]
    zone = "core-automation-zone"

    response = ZoneActions.get(client=client, zone=zone)
    zone_facts = response.data if isinstance(response.data, dict) else {}

    util.deep_merge_in_place(
        zone_facts,
        {
            "Client": client,
            "Zone": zone,
            "AccountFacts": {
                "AwsAccountId": data[P_AUTOMATION_ACCOUNT],
                "Environment": ENVIRONMENT,
            },
            "RegionFacts": {ZONE_REGION_KEY: {"AwsRegion": data[P_REGION]}},
        },
        True,
    )

    ZoneActions.update(**zone_facts)


def register_portfolio(data):

    client = data[P_CLIENT]
    portfolio = data[P_PORTFOLIO]

    response = PortfolioActions.get(client=client, portfolio=portfolio)
    portfolio_facts = response.data if isinstance(response.data, dict) else {}

    portfolio_facts.update(
        {"Client": client, "Portfolio": portfolio, "Owner": data[P_USERNAME]}
    )

    PortfolioActions.update(**portfolio_facts)


def register_app(data):

    client = data[P_CLIENT]
    portfolio = data[P_PORTFOLIO]

    portfoilio_key = f"{client}:{portfolio}"

    app = data[P_APP]
    branch = data[P_BRANCH]
    app_regex = f"^prn:{portfolio}:{app}:{branch}:.*$"

    # Create default tags for app registration
    tags = get_tags(data, app)
    tags.pop(TAG_APP, None)

    response = AppActions.get(ClientPortfolio=portfoilio_key, app=app_regex)
    app_facts = response.data if isinstance(response.data, dict) else {}

    app_facts.update(
        {
            "Client": client,
            "Portfolio": portfolio,
            "Zone": "core-automation-zone",
            "Region": ZONE_REGION_KEY,
            "Tags": tags,
        }
    )

    AppActions.update(**app_facts)


def deploy_database(data, next) -> str:

    client = data[P_CLIENT]
    scope_prefix = data[P_SCOPE]

    # inside the module "core_db" there is a submodule "platform" that contains the template.yaml file, get
    # the real path of the template.yaml file

    db_project_dir = os.path.dirname(os.path.realpath(core_db.platform.__file__))

    # Deploy the FACTS tables
    cprint("\nDEPLOY FACTS DATABASE\n", style="bold underline")

    tags = get_tags(data, "facts")

    data[P_STACK_PARAMETERS] = {
        "ClientsTableName": data[P_CLIENT_TABLE_NAME],
        "PortfoliosTableName": data[P_PORTFOLIOS_TABLE_NAME],
        "AppsTableName": data[P_APPS_TABLE_NAME],
        "ZonesTableName": data[P_ZONES_TABLE_NAME],
        **tags,
    }

    # Save the mater region
    region = data[P_REGION]

    # Set the region to the dynamodb region
    data[P_REGION] = data[P_DYNAMODB_REGION]

    data[P_TEMPLATE] = os.path.join(db_project_dir, "core-automation-db-facts.yaml")
    data[P_STACK_NAME] = f"{scope_prefix}core-automation-db-facts"
    data[P_TAGS] = tags

    # Deploy the FACTS tables region
    start_deploy_stack(**data)

    # Deploy the ITEMS and EVENTS deployment info tables
    cprint("\nDEPLOY DEPLOYMENTS DATABASE\n", style="bold underline")

    tags = get_tags(data, "db")

    data[P_STACK_PARAMETERS] = {
        "ItemTableName": data[P_ITEMS_TABLE_NAME],
        "EventTableName": data[P_EVENTS_TABLE_NAME],
        **tags,
    }

    data[P_TEMPLATE] = os.path.join(db_project_dir, "core-automation-db-items.yaml")
    data[P_STACK_NAME] = f"{scope_prefix}{client}-core-automation-db-items"
    data[P_TAGS] = tags

    start_deploy_stack(**data)

    # Reset the master region
    data[P_REGION] = region

    register_client(data)
    register_zone(data)
    register_portfolio(data)
    register_app(data)

    cprint(
        "\n[bold]WOW!  Good Job![/bold] The Process is complete!\n", style="bold green"
    )

    result = get_input(
        "Press Enter to continue or X to abort.", ["Enter", "x"], "Enter"
    )
    if result.lower() == "x":
        raise Exception("Aborted by user.")

    return next


def pre_database(data, next) -> str:

    cprint("\nDEPLOY DATABASE\n", style="bold underline")

    cprint(
        "The next step will be installing the core automation database.  Please read this note about the database.\n"
    )
    cprint(
        "There are 6 database tables that are deployed in the core automation DynamoDB database.\n"
    )
    cprint("The tables are:\n")

    table = Table(box=box.SIMPLE)
    table.add_column("No.", style="cyan")
    table.add_column("Table", style="cyan")
    table.add_column("Description", style="dark_orange")

    client = data[P_CLIENT]

    clients_table = data[P_CLIENT_TABLE_NAME]
    portfolios_table = data[P_PORTFOLIOS_TABLE_NAME]
    zones_table = data[P_ZONES_TABLE_NAME]
    apps_table = data[P_APPS_TABLE_NAME]
    items_table = data[P_ITEMS_TABLE_NAME]
    events_table = data[P_EVENTS_TABLE_NAME]

    table.add_row(
        "1.",
        clients_table,
        'This table stores client facts and information. A client is an "organization" '
        "and should have a billing/management account.",
    )
    table.add_row(
        "2.",
        zones_table,
        "This table stores zone facts and information.  A zone is a Location where one or more BizApps are deployed."
        "It many time has it's own VPC, subnets, and many times it's own AWS account.",
    )
    table.add_row(
        "3.",
        portfolios_table,
        "This table stores portfolio facts and information.  A portfolio is a collection of deployments. "
        'Many times this is referred to as a "Business Application" or "Project".  You should register apps in a CMDB and'
        "project management system such as Jira or ServiceNow.",
    )
    table.add_row(
        "4.",
        apps_table,
        "This table stores app facts and information.  An app is a Deployment. It is a collectin of resources that make up"
        "all or part of a Business Application. You can register more than one deployment in a portfolio/bizapp.",
    )
    table.add_row(
        "5.",
        items_table,
        "This table stores deployment items.  This is a list of items that are deployed in a deployment.  This is a list of "
        "portfolio, app, branch, build, and component information for the deployment.  You will notice that this table name "
        f'starts with the "{client}" client prefix.  This is because this table is unique to each client.  This is a "client" table.',
    )
    table.add_row(
        "6.",
        events_table,
        "This table stores deployment events.  This is a list of events that are generated during the deployment process."
        "This can be status information, build status, deployment status, release status, etc.  It's a log. You will notice that this table name "
        f'starts with the "{client}" client prefix.  This is because this table is unique to each client.  This is a "client" table.',
    )

    cprint(table)

    result = get_input(
        "Press Enter to continue or X to abort.", ["Enter", "x"], "Enter"
    )
    if result.lower() == "x":
        raise Exception("Aborted by user.")

    return next


def pre_roles(data, next) -> str:

    scope_prefix = data[P_SCOPE]

    cprint("\nDEPLOY ROLES\n", style="bold underline")

    cprint(
        "The next step will be installing the core automation roles.  The roles are:"
    )

    table = Table(box=box.SIMPLE)
    table.add_column("Role", style="cyan")
    table.add_column("Description", style="dark_orange")

    table.add_row(
        f"{scope_prefix}CoreAutomationApiRead",
        "This role is used by users to use the lambda API and DynamoDB.",
    )
    table.add_row(
        f"{scope_prefix}CoreAutomationApiWrite",
        "This role is used by users to write to the API and database.",
    )
    table.add_row(
        f"{scope_prefix}PipelineProvisioning",
        "This role is used by the core automation lambda functions to provision resources.",
    )
    table.add_row(
        f"{scope_prefix}PipelineControl",
        "This role is used by the core automation lambda functions to invoke lambda functions.",
    )

    cprint(table)

    result = get_input(
        "Press Enter to continue or X to abort.", ["Enter", "x"], "Enter"
    )
    if result.lower() == "x":
        raise Exception("Aborted by user.")

    return next


def check_configuration(data, next) -> str:
    cprint("\nCONFIGURATION SETTINGS\n", style="bold underline")

    cprint("The next step will be installing the core automation roles and database.\n")
    cprint("The following illustrates what will be installed:")

    show_configuration(data)

    cprint(
        "\nPlease verify all values above.  If you wish to change them, set the "
        "appropriate environment variables and restart the setup.\n",
        style="bold yellow",
    )

    result = get_input(
        "Press Enter to continue or X to abort.", ["Enter", "x"], "Enter"
    )
    if result.lower() == "x":
        raise Exception("Aborted by user.")

    return next


def check_organization(data, next) -> str:
    cprint("\nCHECK ORGANIZATION\n", style="bold underline")
    cprint(
        "This step checks to see if you have an organization setup in AWS Organizations."
    )

    try:
        org = get_organization_info()
        data[P_ORGANIZATION_ID] = org["Id"]
        data[P_ORGANIZATION_ACCOUNT] = org["AccountId"]
        data[P_ORGANIZATION_NAME] = org["Name"]
        data[P_ORGANIZATION_EMAIL] = org["Email"]
    except Exception:
        cprint(
            "\nYou have not setup an organization in AWS Organizations.\n",
            style="bold red",
        )
        cprint(
            "This process will install SCPs, roles, and other resources in the organization. So, we cannot continue.\n",
            style="yellow",
        )
        raise

    table = Table(box=box.SIMPLE)
    table.add_column("Item", style="cyan")
    table.add_column("Value", style="dark_orange")

    table.add_row("Organization ID", data[P_ORGANIZATION_ID])
    table.add_row("Organization Account", data[P_ORGANIZATION_ACCOUNT])
    table.add_row("Organization Name", data[P_ORGANIZATION_NAME])
    table.add_row("Organization Email", data[P_ORGANIZATION_EMAIL])

    cprint(table)

    result = get_input(
        "Press Enter to continue. or X to abort.", ["Enter", "x"], "Enter"
    )
    if result.lower() == "x":
        raise Exception("Aborted by user.")

    return next


def check_admininistrative_privileges(data, next) -> str:

    cprint("\nCHECK ADMINISTRATIVE PRIVILEGES\n", style="bold underline")
    cprint(
        "This step checks to see if you have administrative privileges in the AWS account.\n"
    )
    cprint(
        "You must have administrative privileges in the AWS account to deploy the core automation\n"
        "resources.  This is because the core automation resources are deployed using CloudFormation\n"
        "with many resources that require administrative permissions.  You must have the ability to\n"
        "deploy templates, setup roles, policy, permissions, and other administrative actions.\n"
    )

    username = data[P_USERNAME]
    current_account = data[P_CURRENT_ACCOUNT]

    is_admin = check_admin_privileges(username)
    if not is_admin:
        raise Exception("You do not have administrative privileges in the AWS account.")

    cprint("You have administrative privileges in the account!\n", style="bold yellow")

    cprint("You are good to go!\n", style="bold green")

    cprint(
        f"We will be installing the core automation resources in the automation account {current_account}.\n"
    )
    cprint(
        "You may be asked to provide additional information about other AWS accounts in your organization.\n"
    )

    result = get_input(
        "If you are ready, press Enter to continue or X to abort.",
        ["Enter", "x"],
        "Enter",
    )

    if result.lower() == "x":
        raise Exception("Aborted by user.")

    return next


def check_profile(data, next) -> str:
    cprint("\nCHECK PROFILE\n", style="bold underline")
    cprint(
        "This step checks to see if you have the AWS profile set in your environment.\n"
    )
    try:
        supplied_profile = data.get(P_AWS_PROFILE)

        data[P_AWS_PROFILE] = aws_profile = util.get_aws_profile()
        data[P_USERNAME] = username = get_iam_user_name()
        data[P_REGION] = region = util.get_region()

    except Exception:
        cprint(
            "There was a problem.  Please check your AWS configuration and try again."
        )
        raise

    identity = data[P_IDENTITY]

    data[P_CURRENT_ACCOUNT] = current_account = identity["Account"]

    if supplied_profile and supplied_profile != aws_profile:
        cprint(
            f'[red]WARNING:[/red] You supplied the AWS_PROFILE "{supplied_profile}" but the AWS CLI is using "{aws_profile}"'
        )
        cprint(
            "You may want to check that the AWS_PROFILE is correct profile before continuing.\n"
        )
        result = get_input(
            "Press Enter to continue or X to abort.", ["Enter", "x"], "Enter"
        )
        if result.lower() == "x":
            raise Exception("Aborted by user.")

        cprint()

    automation_account = util.get_automation_account()

    table = Table(box=box.SIMPLE)
    table.add_column("Item", style="cyan")
    table.add_column("Value", style="dark_orange")
    table.add_column("Environment Variable", style="dark_goldenrod")

    table.add_row("AWS Profile", aws_profile, ENV_AWS_PROFILE)
    table.add_row("Username", username, "")
    table.add_row("Current Account", current_account, "")
    table.add_row("Automation Account", automation_account, ENV_AUTOMATION_ACCOUNT)
    table.add_row("Automation Region", region, ENV_AWS_REGION)

    cprint(table)

    if current_account != data[P_AUTOMATION_ACCOUNT]:
        cprint(
            "\nERROR: Your AWS profile is set to a different account than the automation account.  ",
            style="bold red",
        )
        cprint("\nWhy did yo get this error?\n")
        cprint(
            f"You indicated that your automation account is {data["automation_account"]}.  This\n"
            "is the account where the core automation lambda, database, api, and ui should be\n"
            f"installed but your current account is {current_account}.  You need to pick an\n"
            "AWS_PROFILE with administrative credentials that will allow you to deploy all of\n"
            "the core automation resources in your automation account.\n"
        )
        raise Exception("AWS profile is not set to the automation account.")

    cprint()

    cprint(
        "[green]You are good to go![/green] Your current account is the same as your automation account. [yellow]Good! This is what we want.[/yellow]\n"
    )

    result = get_input(
        "Press Enter to continue or X to abort.", ["Enter", "x"], "Enter"
    )
    if result.lower() == "x":
        raise Exception("Aborted by user.")

    return next


def check_environment(data, next) -> str:
    cprint("\nCHECK ENVIRONMENT\n", style="bold underline")
    cprint(
        "This step checks to see if you have the two required environment variables set.\n"
    )
    cprint("A scoping environment variable:\n")
    cprint(f'  - [cyan]{ENV_SCOPE}[/cyan] = ""\n')
    cprint(
        '            This is a prefix for the resources.  It will defualt to EMPYT "" string \n'
        "            if not set.  You may use this to differentiate core automation installs in\n"
        "            the same AWS account.  If you don't know what to set, leave it empty.\n"
    )
    cprint("The two required environment variables are:\n")
    cprint(f'  - [cyan]{ENV_CLIENT}[/cyan] = "client"\n')
    cprint(
        "            This is the 'slug' or lowercase short name of your organization.\n"
        "            AWS organizations are required. And you must give your organization\n"
        "            a short name that can be references by the core automation system.\n"
        "            The organization is initialized in your billing/management account.\n"
        "            If you don't know what to set, make it a lowercase short name of the\n"
        "            name of your billing/managmeent account.\n"
    )
    cprint(f'  - [cyan]{ENV_AUTOMATION_ACCOUNT}[/cyan] = "123456789012"\n')
    cprint(
        "            This is the AWS account number of the automation account in your organization.\n"
        "            This account where the core automation lambda, database, api, and ui will\n"
        "            be installed.  This account is referred to as the [bold]Automation Account[bold].\n"
        "            This may or may not be the same account as your billing account (The billing\n"
        '            account is also referred to as the [bold]"Management Account"[bold]).\n'
    )
    cprint(
        "[yellow]We will ask about other AWS accounts in later processes of the installation.[white]\n"
    )
    cprint(
        "[yellow]Note:[white] if you are setting up to run the core-automation docker container, these "
    )
    cprint(
        "are the minimum environment variables that must be set in the docker run command.\n"
    )
    cprint("Values:")

    # Load the 3 environment variables from the os environment.
    data[P_SCOPE] = scope_prefix = util.get_automation_scope() or ""
    data[P_CLIENT] = client = os.getenv(ENV_CLIENT)
    data[P_AUTOMATION_ACCOUNT] = automation_account = util.get_automation_account()

    table = Table(box=box.SIMPLE)
    table.add_column("Environment Variable", style="cyan")
    table.add_column("Value", style="dark_orange")
    table.add_column("Status", style="white")

    cresult = "[green]OK[/green]" if client else "[red]ERROR[/red]"
    aresult = "[green]OK[/green]" if automation_account else "[red]ERROR[/red]"

    table.add_row(ENV_SCOPE, scope_prefix, "[green]OK[/green]")
    table.add_row(ENV_CLIENT, client, cresult)
    table.add_row(ENV_AUTOMATION_ACCOUNT, automation_account, aresult)

    cprint(table)

    if cresult != "[green]OK[/green]" or aresult != "[green]OK[/green]":
        cprint("Please set the environment variables and try again.\n")
        cprint(
            "You may use a .env file if you wish. (I could ask you for them now, but, nah.. I'm making you set them up)\n"
        )
        raise Exception(
            "Environment variables not set. Please setup the environment variables and try again."
        )

    result = get_input(
        "Press Enter to continue or X to abort.", ["Enter", "x"], "Enter"
    )
    if result.lower() == "x":
        raise Exception("Aborted by user.")

    return next


def check_aws_cli(data, next) -> str:
    cprint("\nCHECK AWS CLI\n", style="bold underline")
    cprint(
        "This step checks to see that you have he AWS CLI installed and configured\n"
    )

    # check to see that the aws cli is installed in Windows and in Linux

    # run "aws --version" and capture the output
    try:
        result = subprocess.run(
            ["aws", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except FileNotFoundError:
        raise Exception(
            "The AWS CLI is not installed.  Please install the AWS CLI and configure it with the appropriate permissions."
        )

    version = result.stdout.decode("utf-8").strip()

    cprint(f"The AWS CLI is installed: {version}\n")

    get_input("Press Enter to continue")

    return next


def welcome(data, next) -> str:

    if "AWS_ACCESS_KEY_ID" in os.environ:
        del os.environ["AWS_ACCESS_KEY_ID"]
    if "AWS_SECRET_ACCESS_KEY" in os.environ:
        del os.environ["AWS_SECRET_ACCESS_KEY"]

    cprint("\nWELCOME\n", style="bold underline")
    cprint("Welcome to the Core-Automation setup!\n")
    cprint(
        "This setup will guide you through setting up the Core-Automation platform.\n"
    )

    cprint("The platform is dividided into 4 parts:\n")
    cprint("1. Organization Setup")
    cprint("2. Automation Account Setup")
    cprint("3. Audit, Logging, and Compliance Setup")
    cprint("4. Security Monitoring Setup")
    cprint(
        "\nThis setup will perform configuration of item [underline]2 - Automation Account Setup.[/underline]\n"
    )
    cprint(
        "Use the appropriate core command to setup the other parts of the platform.\n"
    )

    cprint(
        "You will need to have the AWS CLI installed and configured with the appropriate permissions to run this command.\n"
    )

    result = get_input(
        "Press Enter to continue or X to abort.", ["Enter", "x"], "Enter"
    )
    if result.lower() == "x":
        raise Exception("Aborted by user.")

    return next


def done(data, next) -> str:
    cprint("Setup is complete")

    return next


# The steps to setup the core automation platform
# step_name -> (function, next_step_name)
STEPS: dict[str, tuple[Callable, str]] = {
    "welcome": (welcome, "check_aws_cli"),
    "check_aws_cli": (check_aws_cli, "env"),
    "env": (check_environment, "profile"),
    "profile": (check_profile, "admin"),
    "admin": (check_admininistrative_privileges, "org"),
    "org": (check_organization, "config"),
    "config": (check_configuration, "pre_roles"),
    "pre_roles": (pre_roles, "roles"),
    "roles": (deploy_roles, "pre_db"),
    "pre_db": (pre_database, "db"),
    "db": (deploy_database, "pre_storage"),
    "pre_storage": (pre_storage, "storage"),
    "storage": (deploy_storage, "done"),
    "done": (done, "quit"),
}


def get_description() -> str:
    return """Bootstrap the Core-Automation Platform.

This command will setup/bootstrap the Core-Automation platform.

You will need to have the AWS CLI installed and configured with the appropriate permissions to run this command.

Environment Variables Required:

    CLIENT=<name>
    AUTOMATION_ACCOUNT=<account_number>

CLINET is the short 'slug' name of your organization.  Example: "acme" or "myorg".

This represents your organization in AWS Organizations.

AUTOMATION_ACCOUNT is the AWS account number of the account where the core automation resources will be installed/bootstrapped.

CLIENT and AUTOMATION_ACCOUNT environment variables can be defined with

# core --client <name> bootstrap --account <automation_account>

"""


def get_bootstrap_command(parser) -> ExecuteCommandsType:

    description = "Bootstrap the Core-Automation platform"
    p = parser.add_parser("bootstrap", help=description, description=get_description())
    p.add_argument(
        "-a, --account",
        dest=P_AUTOMATION_ACCOUNT,
        metavar="<account_number>",
        help="The automation account number",
    )
    return {"bootstrap": (description, execute_setup)}


def execute_setup(**kwargs):
    step = "welcome"
    try:
        while step != "quit":
            fn = STEPS[step][0]
            next = STEPS[step][1]
            step = fn(kwargs, next)
        return 0
    except KeyboardInterrupt:
        cprint("Aborted by user.")
        return 1
    except Exception as e:
        cprint(f"Error: {e}", style="bold red")
        cprint()
        return 1
