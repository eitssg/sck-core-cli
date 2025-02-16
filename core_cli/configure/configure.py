""" Configuration Module Package .env file and context """

from typing import Callable
from rich.table import Table
from rich import box

import core_framework as util
import core_db as db

from core_framework.constants import (  # noqa: F401
    P_AWS_PROFILE,
    P_AWS_REGION,
    P_SCOPE,
    P_CLIENT,
    P_CLIENT_NAME,
    P_DOMAIN,
    P_CLIENT_REGION,
    P_USERNAME,
    P_CURRENT_ACCOUNT,
    P_CDK_DEFAULT_ACCOUNT,
    P_CDK_DEFAULT_REGION,
    P_IAM_ACCOUNT,
    P_AUTOMATION_ACCOUNT,
    P_SECURITY_ACCOUNT,
    P_AUDIT_ACCOUNT,
    P_NETWORK_ACCOUNT,
    P_REGION,
    P_DOCUMENT_BUCKET_NAME,
    P_UI_BUCKET_NAME,
    P_ARTEFACT_BUCKET_NAME,
    P_BUCKET_NAME,
    P_BUCKET_REGION,
    P_TEMPLATE,
    P_STACK_NAME,
    P_STACK_PARAMETERS,
    P_ORGANIZATION_ID,
    P_ORGANIZATION_NAME,
    P_ORGANIZATION_EMAIL,
    P_ORGANIZATION_ACCOUNT,
    P_AUTOMATION_TYPE,
    P_TASKS,
    P_UNITS,
    P_PORTFOLIO,
    P_APP,
    P_BRANCH,
    P_BUILD,
    P_COMPONENT,
    P_ENVIRONMENT,
    P_DYNAMODB_HOST,
    P_DYNAMODB_REGION,
    P_LOG_AS_JSON,
    P_VOLUME,
    P_LOG_DIR,
    P_DELIVERED_BY,
    P_LOCAL_MODE,
    P_USE_S3,
    P_ENFORCE_VALIDATION,
    P_INVOKER_ARN,
    P_INVOKER_NAME,
    P_INVOKER_REGION,
    P_API_LAMBDA_ARN,
    P_API_LAMBDA_NAME,
    P_API_HOST_URL,
    P_EXECUTE_LAMBDA_ARN,
    P_START_RUNNER_LAMBDA_ARN,
    P_DEPLOYSPEC_COMPILER_LAMBDA_ARN,
    P_COMPONENT_COMPILER_LAMBDA_ARN,
    P_START_RUNNER_STEP_FUNCTION_ARN,
    P_CORRELATION_ID,
    P_TAGS,
    P_PROJECT,
    P_BIZAPP,
    P_CLIENT_TABLE_NAME,
    P_PORTFOLIOS_TABLE_NAME,
    P_APPS_TABLE_NAME,
    P_ZONES_TABLE_NAME,
    P_ITEMS_TABLE_NAME,
    P_EVENTS_TABLE_NAME,
    P_CONSOLE_LOG,
    P_CONSOLE,
    P_LOG_LEVEL,
    V_DEPLOYSPEC,
    V_PIPELINE,
    CTX_CONTEXT,
    ENV_LOG_LEVEL,
)

from ..console import cprint, get_input, jprint
from .client_config import get_client_context
from ..environment import (
    get_arguments_from_env,
    args_to_env,
    get_dotenv_config,
    set_environment_from_args,
)


def get_arguments_from_facts(facts: dict[str, str | None]) -> dict[str, str]:
    """Get the arguments from the facts.  return only Non-empty values"""

    # assicate each property in the client FACTS database with the P_ value
    # You'll notice that the P_ values are the same as the keys in the FACTS database but in snake_case
    items_map = {
        "Scope": P_SCOPE,
        "Client": P_CLIENT,
        "ClientRegion": P_CLIENT_REGION,
        "ClientName": P_CLIENT_NAME,
        "OrganizationId": P_ORGANIZATION_ID,
        "OrganizationName": P_ORGANIZATION_NAME,
        "OrganizationAccount": P_ORGANIZATION_ACCOUNT,
        "OrganizationEmail": P_ORGANIZATION_EMAIL,
        "Domain": P_DOMAIN,
        "IamAccount": P_IAM_ACCOUNT,
        "AuditAccount": P_AUDIT_ACCOUNT,
        "MasterRegion": P_REGION,
        "DocsBucketName": P_DOCUMENT_BUCKET_NAME,
        "UiBucketName": P_UI_BUCKET_NAME,
        "BucketName": P_BUCKET_NAME,
        "BucketRegion": P_BUCKET_REGION,
        "AutomationAccount": P_AUTOMATION_ACCOUNT,
        "ArtefactBucketName": P_ARTEFACT_BUCKET_NAME,
        "SecurityAccount": P_SECURITY_ACCOUNT,
        "NetworkAccount": P_NETWORK_ACCOUNT,
    }

    args: dict[str, str] = {}
    for k, v in facts.items():
        arg_key = items_map.get(k)
        if arg_key and v:
            args[arg_key] = v
    return args


def update_core_config(**kwargs):
    """Make changes to and update the core configuration file."""

    client = kwargs.get(P_CLIENT)
    aws_profile = kwargs.get(P_AWS_PROFILE)
    username = kwargs.get(P_USERNAME)

    cprint("Core Automation Configuration\n", style="bold underline")
    cprint(f"AWS Profile: [green]{aws_profile}[/green]")
    cprint(f"Client: [green]{client}[/green]")
    cprint(f"Username: [green]{username}[/green]\n")

    # Pull facts from the current context or the client FACTS database if a context is not found
    # The priority of reading values from the database is:
    # facts database -> context configuration file -> environment variables -> commandline parameter

    # This should be done on application startup/exection.  So, it's only here temporarily.
    facts = get_client_context(kwargs)
    facts_paramters = get_arguments_from_facts(facts)
    set_environment_from_args(facts_paramters)

    # Get only the .env overrides.  The .env would have already been loaded into os.environ at this point.
    env = get_dotenv_config()
    config = get_arguments_from_env(env)

    # prompt for each P_ value
    # (description, choices, key, derrived_value_factory)
    prompts_keys = [
        (
            "AWS Profile for this application. [red]REQUIRED[/red]",
            None,
            P_AWS_PROFILE,
            util.get_aws_profile,
        ),
        (
            "AWS Region for this application (this can default from your AWS Cli configuration) ",
            None,
            P_AWS_REGION,
            util.get_region,
        ),
        (
            "Client slug (short name to identify the client) [red]REQUIRED[/red]",
            None,
            P_CLIENT,
            util.get_client,
        ),
        (
            "Scope prefix (different context in the same automation account) ",
            None,
            P_SCOPE,
            util.get_automation_scope,
        ),
        (
            "Client name (such as the management account name)",
            None,
            P_CLIENT_NAME,
            util.get_client_name,
        ),
        (
            "Default client region (where your organization is located)",
            None,
            P_CLIENT_REGION,
            util.get_client_region,
        ),
        (
            "Domain name (used for the domain name of the appliation)",
            None,
            P_DOMAIN,
            util.get_domain,
        ),
        (
            "Automation/Cloud Services AWS Account ID [red]REQUIRED[/red]",
            None,
            P_AUTOMATION_ACCOUNT,
            util.get_automation_account,
        ),
        (
            "Region where the automation engine is deployed and run",
            None,
            P_REGION,
            util.get_region,
        ),
        (
            "Organization/Billing/Control Tower/SSO account",
            None,
            P_ORGANIZATION_ACCOUNT,
            util.get_organization_account,
        ),
        (
            "AWS Organization ID ",
            None,
            P_ORGANIZATION_ID,
            util.get_organization_id,
        ),
        (
            "Audit/Log/Cloudwatch/KMS/Secrets Account (shared For Zones)",
            None,
            P_AUDIT_ACCOUNT,
            util.get_audit_account,
        ),
        (
            "Security Hub/Guard Duty/SEIM Account",
            None,
            P_SECURITY_ACCOUNT,
            util.get_security_account,
        ),
        (
            "Network/Transit Gateway/VPN Account/VPC's/Firewalls",
            None,
            P_NETWORK_ACCOUNT,
            util.get_network_account,
        ),
        (
            "AWS Account ID for Identity Management (IAM)",
            None,
            P_IAM_ACCOUNT,
            util.get_iam_account,
        ),
        (
            "Automation Documentation Bucket Name (in S3)",
            None,
            P_DOCUMENT_BUCKET_NAME,
            util.get_document_bucket_name,
        ),
        (
            "Automation Browser UI Bucket Name (in S3)",
            None,
            P_UI_BUCKET_NAME,
            util.get_ui_bucket_name,
        ),
        (
            "Deployed Apps Artefacts Bucket Name (in S3)",
            None,
            P_ARTEFACT_BUCKET_NAME,
            util.get_artefact_bucket_name,
        ),
        (
            "Deployment Packages Bucket Name (in S3)",
            None,
            P_BUCKET_NAME,
            util.get_bucket_name,
        ),
        (
            "Automation Artefacts/Packages Bucket Region (in S3)",
            None,
            P_BUCKET_REGION,
            util.get_bucket_region,
        ),
        (
            "AWS Oranization Name (AWS Management Account Name)",
            None,
            P_ORGANIZATION_NAME,
            util.get_organization_name,
        ),
        (
            "AWS Oranization Email (AWS Management Account Email)",
            None,
            P_ORGANIZATION_EMAIL,
            util.get_organization_email,
        ),
        (
            f"Default type of deployment ({V_DEPLOYSPEC} or {V_PIPELINE})",
            ["-", V_DEPLOYSPEC, V_PIPELINE],
            P_AUTOMATION_TYPE,
            util.get_automation_type,
        ),
        (
            "Default portfolio/bizapp slug (short name to identify the portfolio)",
            None,
            P_PORTFOLIO,
            util.get_portfolio,
        ),
        (
            "Default app slug (short name to identify the deployment part of the portfolio application)",
            None,
            P_APP,
            util.get_app,
        ),
        (
            "Default branch (git branch)",
            None,
            P_BRANCH,
            util.get_branch,
        ),
        (
            "Default build number (version or git commit hash) (no period allowed. Enter v1-0-0 for version v1.0.0)",
            None,
            P_BUILD,
            util.get_build,
        ),
        (
            "Default evnrionment name (PRD, DEV, STAGE, SIT, etc)",
            None,
            P_ENVIRONMENT,
            util.get_environment,
        ),
        (
            "Dynamodb Host URL (Useful for local mode. e.g. http://localhost:8000)",
            None,
            P_DYNAMODB_HOST,
            util.get_dynamodb_host,
        ),
        (
            "Dynamodb Table Region",
            None,
            P_DYNAMODB_REGION,
            util.get_dynamodb_region,
        ),
        (
            'Local mode.  Use "True" for docker containers and you don\'t want to use lambda functions (True/False)',
            None,
            P_LOCAL_MODE,
            util.is_local_mode,
        ),
        (
            'Use S3 for storage even in Local mode (True/False).  If "True" the VOLUME configuration is ignored.',
            ["-", "true", "false"],
            P_USE_S3,
            util.is_use_s3,
        ),
        (
            "Storage Region of Packages and Artefacts S3 Bucket",
            None,
            P_BUCKET_REGION,
            util.get_bucket_region,
        ),
        (
            "Data Storage volume/directory if not using S3 for storage. (e.g. `N:\\data`, or `/mnt/data` or S3 URL)\n"
            "If USE_S3 is True this value is ignored and will respond with th S3 URL.",
            None,
            P_VOLUME,
            util.get_storage_volume,
        ),
        (
            "Log as JSON when outputting to console log or file logs",
            None,
            P_LOG_AS_JSON,
            util.is_json_log,
        ),
        (
            "Log to the CLI Console (True/False)",
            ["-", "true", "false"],
            P_CONSOLE_LOG,
            util.is_console_log,
        ),
        (
            "Log Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            ["-", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            P_LOG_LEVEL,
            util.get_log_level,
        ),
        (
            'Execute actions interactively or in the background?.  Enter the value "interactive" or "non-interactive"',
            ["-", "interactive", "non-interactive"],
            P_CONSOLE,
            util.get_console_mode,
        ),
        (
            "Log directory for log files. (e.g. /mnt/data/logs). Used to output logs to a file on your mount volume.",
            None,
            P_LOG_DIR,
            util.get_log_dir,
        ),
        (
            'Delivered by (name of the person or team. e.g. "DevOps Team")',
            None,
            P_DELIVERED_BY,
            util.get_delivered_by,
        ),
        (
            "Enforce validation of the deployment specification",
            None,
            P_ENFORCE_VALIDATION,
            util.is_enforce_validation,
        ),
        (
            "Override the Invoker Lambda function ARN",
            None,
            P_INVOKER_ARN,
            util.get_invoker_lambda_arn,
        ),
        (
            "Override the Invoker Lambda function name",
            None,
            P_INVOKER_NAME,
            util.get_invoker_lambda_name,
        ),
        (
            "Override the Invoker Lambda function region",
            None,
            P_INVOKER_REGION,
            util.get_invoker_lambda_region,
        ),
        (
            "Override the API Lambda function ARN",
            None,
            P_API_LAMBDA_ARN,
            util.get_api_lambda_arn,
        ),
        (
            "Override the API Lambda function name",
            None,
            P_API_LAMBDA_NAME,
            util.get_api_lambda_name,
        ),
        (
            'URL of the API Host (e.g. https://api.example.com).  Please note that if you set this value and "example.com"\n'
            "is hosted in Route53 the system will attempt to ensure the CNAME is entered for the API Gateway",
            None,
            P_API_HOST_URL,
            util.get_api_host_url,
        ),
        (
            "The Execute Actions/Scripts Lambda function ARN",
            None,
            P_EXECUTE_LAMBDA_ARN,
            util.get_execute_lambda_arn,
        ),
        (
            "Override the Step-Function Start Runner Lambda function ARN",
            None,
            P_START_RUNNER_LAMBDA_ARN,
            util.get_start_runner_lambda_arn,
        ),
        (
            "DeploySpec Compiler Lambda ARN Description",
            None,
            P_DEPLOYSPEC_COMPILER_LAMBDA_ARN,
            util.get_deployspec_compiler_lambda_arn,
        ),
        (
            "Component Compiler Lambda ARN Description",
            None,
            P_COMPONENT_COMPILER_LAMBDA_ARN,
            util.get_component_compiler_lambda_arn,
        ),
        (
            "Runner Step Function ARN Description",
            None,
            P_START_RUNNER_STEP_FUNCTION_ARN,
            util.get_start_runner_lambda_arn,
        ),
        (
            "Default Project (Jira/GitHub project name) Name associated with the Application deployment",
            None,
            P_PROJECT,
            util.get_project,
        ),
        (
            "Default Business Application Name (relates to Portfolio).  What's the name in your CMDB?",
            None,
            P_BIZAPP,
            util.get_bizapp,
        ),
        (
            "Default Client/AWS Organization FACTS DynamoDB Table Name",
            None,
            P_CLIENT_TABLE_NAME,
            db.get_clients_table_name,
        ),
        (
            "Default Portfolio (Business Application) FACTS DynamoDB Table Name",
            None,
            P_PORTFOLIOS_TABLE_NAME,
            db.get_portfolios_table_name,
        ),
        (
            "Default Apps (Deployments) FACTS DynamoDB Table Name",
            None,
            P_APPS_TABLE_NAME,
            db.get_apps_table_name,
        ),
        (
            "Default Landing Zones FACTS DynamoDB Table Name",
            None,
            P_ZONES_TABLE_NAME,
            db.get_zones_table_name,
        ),
        (
            "Default Deployment Instances DynamoDB Table Name",
            None,
            P_ITEMS_TABLE_NAME,
            db.get_items_table_name,
        ),
        (
            "Default Deployment Events DynamoDB Table Name ",
            None,
            P_EVENTS_TABLE_NAME,
            db.get_events_table_name,
        ),
    ]

    cprint(f"\nEnter configuration values for client: {client}\n")

    num_of_options = len(prompts_keys)
    for i, v in enumerate(prompts_keys):
        description, choices, key, factory = v
        prompt = f"({i + 1}/{num_of_options}) Enter override"
        if choices:
            prompt += " (dash (-) for None)"
        else:
            prompt += " (dash (-) removes the value)"
        set_config_value(config, description, prompt, choices, key, factory)
        cprint("")

    print("OK, we are done.\n\nHere is the configuration we have for you:\n")

    show_config(config)
    show_config_as_json(config)
    show_config_as_env(config)

    save_env_file(config)


def show_config_as_json(config):

    # Convert config to context (keys converted from snake_case to PascalCase)
    context = {to_pascal_case(k): v for k, v in config.items()}

    jprint(util.to_json({CTX_CONTEXT: context}))


def show_config(config):

    # Convert config to context (keys converted from snake_case to PascalCase)
    context = {to_pascal_case(k): v for k, v in config.items()}

    table = Table(title="Context Settings", box=box.SIMPLE)
    table.add_column("Key", style="bold")
    table.add_column("Value", style="bold")

    for k, v in context.items():
        table.add_row(k, v)

    cprint(table)


def show_config_as_env(config):

    env_values = args_to_env(config)

    table = Table(title="Environment Variables", box=box.SIMPLE)
    table.add_column("Key", style="bold")
    table.add_column("Value", style="bold")

    for k, v in env_values.items():
        table.add_row(k, v)

    cprint(table)


def save_env_file(config):

    env_values = args_to_env(config)

    for k, v in env_values.items():
        print(f'{k}="{v}"')


def to_pascal_case(snake_str: str) -> str:
    """Convert a snake_case string to PascalCase"""
    return "".join(word.title() for word in snake_str.split("_"))


def set_config_value(
    config: dict,
    description: str,
    prompt: str,
    choices: list[str],
    key: str,
    current_value_factory: Callable,
):
    """Set a value in the configuration file"""

    current_value = current_value_factory()
    current_override = config.get(key)

    if description:
        cprint(description)
        cprint(f"Current derrived value: [green]{current_value}[/green]")

    value = get_input(prompt, choices, current_override)

    if value == "-":
        config.pop(key, None)
        # BUG: Please note there is a bug here.  I cannot determine if the environment varialbe
        # was set in the .env file or by the operating system.  So, removing it for the purposes
        # of configuration is at risk of an unknown consiquence.
        # See the environment.py file for more details
        set_environment_from_args({key: None}, remove_none=True)
    elif value:
        config[key] = value
        set_environment_from_args({key: value})


def get_configure_command(subparsers):
    """Get the parser for the configuration command"""

    description = "Configure the core subsystem client vars"

    cp = subparsers.add_parser(
        "config",
        description=description,
        help=description,
    )
    cp.set_group_title(0, "Configure actions")
    cp.set_group_title(1, "Available options")

    return {"config": (description, update_core_config)}
