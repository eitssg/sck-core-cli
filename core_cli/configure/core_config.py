"""Manage the ~/core/config configuration file"""

import core_framework as util
import core_db as db

from ..console import cprint, get_input
from .client_config import get_client_config_file
from core_framework.constants import (
    P_AWS_PROFILE,
    P_AWS_REGION,
    P_SCOPE,
    P_CLIENT,
    P_CLIENT_NAME,
    P_DOMAIN,
    P_CLIENT_REGION,
    P_ORGANIZATION_ID,
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
    P_MASTER_REGION,
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
    P_RUNNER_STEP_FUNCTION_ARN,
    P_TAGS,
    P_PROJECT,
    P_BIZAPP,
    P_CLIENT_TABLE_NAME,
    P_PORTFOLIOS_TABLE_NAME,
    P_APPS_TABLE_NAME,
    P_ZONES_TABLE_NAME,
    P_ITEMS_TABLE_NAME,
    P_EVENTS_TABLE_NAME,
)


def update_core_config(**kwargs):
    """Make changes to and update the core configuration file."""

    client = kwargs.get(P_CLIENT)
    aws_profile = kwargs.get(P_AWS_PROFILE)

    cprint("Core Automation Configuration\n", style="bold undeerline")
    cprint(f"AWS Profile: [green]{aws_profile}[/green]\n")

    config = get_client_config_file(kwargs)

    # prompt for each P_ value
    prompts_keys = [
        (
            "AWS Profile Description",
            "AWS Profile for this application [{}]: ",
            P_AWS_PROFILE,
            util.get_aws_profile,
        ),
        (
            "AWS Region Description",
            "AWS Region for this application (this can default from your AWS Cli configuration) [{}]: ",
            P_AWS_REGION,
            util.get_region,
        ),
        (
            "Client Slug Description",
            "Client slug (short name to identify the client)            [{}]: ",
            P_CLIENT,
            util.get_client,
        ),
        (
            "Scope Prefix Description",
            "Scope prefix (different context in the same automation account) [{}]: ",
            P_SCOPE,
            util.get_automation_scope,
        ),
        (
            "Client Name Description",
            "Client name (such as the management account name)          [{}]: ",
            P_CLIENT_NAME,
            util.get_client_name,
        ),
        (
            "Default Client Region Description",
            "Default client region (where your organization is located)  [{}]: ",
            P_CLIENT_REGION,
            util.get_client_region,
        ),
        (
            "Domain Name Description",
            "Domain name (used for the domain name of the appliation)   [{}]: ",
            P_DOMAIN,
            util.get_domain,
        ),
        (
            "Automation Account Description",
            "Automation (Build) account                                 [{}]: ",
            P_AUTOMATION_ACCOUNT,
            util.get_automation_account,
        ),
        (
            "Automation Region Description",
            "Automation (Build) region of the engine and CMDB database  [{}]: ",
            P_MASTER_REGION,
            util.get_automation_region,
        ),
        (
            "Bucket Region Description",
            "Automation (Build) region of the FACTS/Artefacts S3 bucket [{}]: ",
            P_BUCKET_REGION,
            util.get_bucket_region,
        ),
        (
            "Organization Account Description",
            "Organization/Billing/Control Tower/SSO account             [{}]: ",
            P_ORGANIZATION_ACCOUNT,
            util.get_organization_account,
        ),
        (
            "Organization ID Description",
            "Organization id                                            [{}]: ",
            P_ORGANIZATION_ID,
            util.get_organization_id,
        ),
        (
            "Audit Account Description",
            "Audit/Log/Cloudwatch/KMS/Secrets Account (shared For Zones) [{}]: ",
            P_AUDIT_ACCOUNT,
            util.get_audit_account,
        ),
        (
            "Security Account Description",
            "Security Hub/Guard Duty/SEIM Account                       [{}]: ",
            P_SECURITY_ACCOUNT,
            util.get_security_account,
        ),
        (
            "Network Account Description",
            "Network/Transit Gateway/VPN Account/VPC's/Firewalls        [{}]: ",
            P_NETWORK_ACCOUNT,
            util.get_network_account,
        ),
        (
            "IAM Account Description",
            "AWS Account ID for Identity Management(IAM)                [{}]: ",
            P_IAM_ACCOUNT,
            util.get_iam_account,
        ),
        (
            "Automation Account Description",
            "AWS Account ID for Automation (Build)                      [{}]: ",
            P_AUTOMATION_ACCOUNT,
            util.get_automation_account,
        ),
        (
            "Security Account Description",
            "AWS Account ID for Security Hub/Guard Duty/SEIM            [{}]: ",
            P_SECURITY_ACCOUNT,
            util.get_security_account,
        ),
        (
            "Document Bucket Name Description",
            "Automation Documeation Bucket Name (in S3)                [{}]: ",
            P_DOCUMENT_BUCKET_NAME,
            util.get_document_bucket_name,
        ),
        (
            "UI Bucket Name Description",
            "Automation Browser UI Bucket Name (in S3)                [{}]: ",
            P_UI_BUCKET_NAME,
            util.get_ui_bucket_name,
        ),
        (
            "Artefact Bucket Name Description",
            "Automation Artefacts Bucket Name (in S3)                [{}]: ",
            P_ARTEFACT_BUCKET_NAME,
            util.get_artefact_bucket_name,
        ),
        (
            "Bucket Name Description",
            "Automation Packages Bucket Name (in S3)                [{}]: ",
            P_BUCKET_NAME,
            util.get_bucket_name,
        ),
        (
            "Bucket Region Description",
            "Automation Artefacts/Packages Bucket Region (in S3)    [{}]: ",
            P_BUCKET_REGION,
            util.get_bucket_region,
        ),
        (
            "Organization Name Description",
            "AWS Oranization Name (AWS Management Account Name)    [{}]: ",
            P_ORGANIZATION_NAME,
            util.get_organization_name,
        ),
        (
            "Organization Email Description",
            "AWS Oranization Email (AWS Management Account Email)    [{}]: ",
            P_ORGANIZATION_EMAIL,
            util.get_organization_email,
        ),
        (
            "Automation Type Description",
            "Default type of deployment ({V_DEPLOYSPEC} or {VPIPELINE}) [{}]: ",
            P_AUTOMATION_TYPE,
            util.get_automation_type,
        ),
        (
            "Portfolio Description",
            "Default portfolio/bizapp slug (short name to identify the portfolio) [{}]: ",
            P_PORTFOLIO,
            util.get_portfolio,
        ),
        (
            "Application Description",
            "Default application slug (short name to identify the application) [{}]: ",
            P_APP,
            util.get_app,
        ),
        (
            "Branch Description",
            "Default branch (git branch) [{}]: ",
            P_BRANCH,
            util.get_branch,
        ),
        (
            "Build Description",
            "Default build number (git commit hash) [{}]: ",
            P_BUILD,
            util.get_build,
        ),
        (
            "Environment Description",
            "Default evnrionment name (PRD, DEV, STAGE, SIT, etc) [{}]: ",
            P_ENVIRONMENT,
            util.get_environment,
        ),
        (
            "Dynamodb Host Description",
            "Dynamodb Host Name overrride [{}]: ",
            P_DYNAMODB_HOST,
            util.get_dynamodb_host,
        ),
        (
            "Dynamodb Region Description",
            "Dynamodb Region Name override [{}]: ",
            P_DYNAMODB_REGION,
            util.get_dynamodb_region,
        ),
        (
            "Local Mode Description",
            'Local mode.  Use "True" for docker containers and you don\'t wanto to use lambda functions (True/False) [{}]: ',
            P_LOCAL_MODE,
            util.is_local_mode,
        ),
        (
            "Use S3 Description",
            'Use S3 for storage even in Local mode (True/False).  If "True" the VOLUMNE configuration is [{}]: ',
            P_USE_S3,
            util.is_use_s3,
        ),
        (
            "Volume Description",
            "Data Storage volume/directory if NOT using S3 for storage [{}]: ",
            P_VOLUME,
            util.get_storage_volume,
        ),
        (
            "Log as JSON Description",
            "Log as JSON when outputting to console log or file logs [{}]: ",
            P_LOG_AS_JSON,
            util.is_json_log,
        ),
        (
            "Log Directory Description",
            "Log directory for log files [{}]: ",
            P_LOG_DIR,
            util.get_log_dir,
        ),
        (
            "Delivered By Description",
            "Delivered by (name of the person or team) [{}]: ",
            P_DELIVERED_BY,
            util.get_delivered_by,
        ),
        (
            "Enforce Validation Description",
            "Enforce validation of the deployment specification [{}]: ",
            P_ENFORCE_VALIDATION,
            util.is_enforce_validation,
        ),
        (
            "Invoker Lambda ARN Description",
            "Override the Invoker Lambda function ARN [{}] ",
            P_INVOKER_ARN,
            util.get_invoker_lambda_arn,
        ),
        (
            "Invoker Lambda Name Description",
            "Override the Invoker Lambda function name [{}] ",
            P_INVOKER_NAME,
            util.get_invoker_lambda_name,
        ),
        (
            "Invoker Lambda Region Description",
            "Override the Invoker Lambda function region [{}] ",
            P_INVOKER_REGION,
            util.get_invoker_lambda_region,
        ),
        (
            "API Lambda ARN Description",
            "Override the API Lambda function ARN [{}] ",
            P_API_LAMBDA_ARN,
            util.get_api_lambda_arn,
        ),
        (
            "API Lambda Name Description",
            "Override the API Lambda function name [{}] ",
            P_API_LAMBDA_NAME,
            util.get_api_lambda_name,
        ),
        (
            "API Host URL Description",
            "Override the API Host URL [{}] ",
            P_API_HOST_URL,
            util.get_api_host_url,
        ),
        (
            "Execute Lambda ARN Description",
            "Override the Execute Actions/Scripts Lambda function ARN [{}] ",
            P_EXECUTE_LAMBDA_ARN,
            util.get_execute_lambda_arn,
        ),
        (
            "Start Runner Lambda ARN Description",
            "Override the Step-Function Start Runner Lambda function ARN [{}] ",
            P_START_RUNNER_LAMBDA_ARN,
            util.get_start_runner_lambda_arn,
        ),
        (
            "DeploySpec Compiler Lambda ARN Description",
            "Override the DeploySpec Compiler Lambda function ARN [{}] ",
            P_DEPLOYSPEC_COMPILER_LAMBDA_ARN,
            util.get_deployspec_compiler_lambda_arn,
        ),
        (
            "Component Compiler Lambda ARN Description",
            "Override the Component Compiler Lambda function ARN [{}] ",
            P_COMPONENT_COMPILER_LAMBDA_ARN,
            util.get_component_compiler_lambda_arn,
        ),
        (
            "Runner Step Function ARN Description",
            "Override the Runner Step Function ARN [{}] ",
            P_RUNNER_STEP_FUNCTION_ARN,
            util.get_runner_step_function_arn,
        ),
        (
            "Project Description",
            "Default Project Name [{}] ",
            P_PROJECT,
            util.get_project,
        ),
        (
            "Business Application Description",
            "Default Business Application Name (relates to Portfolio) [{}] ",
            P_BIZAPP,
            util.get_bizapp,
        ),
        (
            "Client Table Name Description",
            "Default Client FACTS DynamoDB Table Name [{}] ",
            P_CLIENT_TABLE_NAME,
            util.get_client_table_name,
        ),
        (
            "Portfolio Table Name Description",
            "Default Portfolio FACTS DynamoDB Table Name [{}] ",
            P_PORTFOLIOS_TABLE_NAME,
            util.get_portfolios_table_name,
        ),
        (
            "Apps Table Name Description",
            "Default Apps FACTS DynamoDB Table Name [{}] ",
            P_APPS_TABLE_NAME,
            util.get_apps_table_name,
        ),
        (
            "Zones Table Name Description",
            "Default Zones FACTS DynamoDB Table Name [{}] ",
            P_ZONES_TABLE_NAME,
            util.get_zones_table_name,
        ),
        (
            "Deployments Table Name Description",
            "Default Deployments DynamoDB Table Name [{}] ",
            P_ITEMS_TABLE_NAME,
            util.get_items_table_name,
        ),
        (
            "Events Table Name Description",
            "Default Deployment Events DynamoDB Table Name [{}] ",
            P_EVENTS_TABLE_NAME,
            util.get_events_table_name,
        ),
    ]

    cprint(f"\nEnter configuration values for client: {client}\n")

    for description, prompt, key, default_factory in prompts_keys:
        set_config_value(config, description, prompt, key, default_factory)

    print("OK, we are done.\n\nHere is the configuration we have for you:\n")


def set_config_value(config: dict, description, prompt, key, default_factory):
    """Set a value in the configuration file"""

    default_value = default_factory()

    if description:
        cprint(description)
        value = config.get(key)
        if value:
            cprint(f"Current override value: [green]{value}[/green]")
        cprint(f"Current derrived value: [green]{default_value}[/green]")

    cprint("Enter a dash (-) to remove the value")

    value = get_input(prompt.format(default_value), None, default_value)

    if value == "-":
        config.pop(key)
    elif value:
        config[key] = value
