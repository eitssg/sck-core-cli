""" Manage the environment.  This is the FIRST module that is loade from the command line """

import gettext
import os

from rich.table import Table
from rich import box
import dotenv

# see the BUG in the configration module.
# I need to keep track of what ENV variables were set in the .env file and which
# were set be the OS.  I have not done so yet.
dotenv.load_dotenv(override=True)


# Initialize the translation function
def setup_i18n(locale: str = "en"):
    locales_dir = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "locale"
    )
    gettext.bindtextdomain("messages", locales_dir)
    gettext.textdomain("messages")
    translation = gettext.translation(
        "messages", locales_dir, languages=[locale], fallback=True
    )
    translation.install()
    return translation.gettext


_ = setup_i18n()

# console loads models and models REQUIRES the os.envrion be set.  Dumb
from .console import cprint  # noqa: E402

from core_framework.constants import (  # noqa: E402
    ENV_AWS_PROFILE,
    ENV_AWS_REGION,
    ENV_TASKS,
    ENV_UNITS,
    ENV_AUTOMATION_TYPE,
    ENV_CLIENT_REGION,
    ENV_CLIENT_NAME,
    ENV_CLIENT,
    ENV_SCOPE,
    ENV_PORTFOLIO,
    ENV_APP,
    ENV_BRANCH,
    ENV_BUILD,
    ENV_COMPONENT,
    ENV_ENVIRONMENT,
    ENV_BUCKET_NAME,
    ENV_BUCKET_REGION,
    ENV_INVOKER_LAMBDA_ARN,
    ENV_INVOKER_LAMBDA_NAME,
    ENV_INVOKER_LAMBDA_REGION,
    ENV_API_LAMBDA_ARN,
    ENV_API_LAMBDA_NAME,
    ENV_API_HOST_URL,
    ENV_DYNAMODB_REGION,
    ENV_DYNAMODB_HOST,
    ENV_EXECUTE_LAMBDA_ARN,
    ENV_START_RUNNER_LAMBDA_ARN,
    ENV_DEPLOYSPEC_COMPILER_LAMBDA_ARN,
    ENV_COMPONENT_COMPILER_LAMBDA_ARN,
    ENV_MASTER_REGION,
    ENV_AUTOMATION_ACCOUNT,
    ENV_ORGANIZATION_ACCOUNT,
    ENV_ORGANIZATION_EMAIL,
    ENV_ORGANIZATION_ID,
    ENV_ORGANIZATION_NAME,
    ENV_ARTEFACT_BUCKET_NAME,
    ENV_LOG_AS_JSON,
    ENV_VOLUME,
    ENV_LOG_DIR,
    ENV_DELIVERED_BY,
    ENV_LOCAL_MODE,
    ENV_USE_S3,
    ENV_ENFORCE_VALIDATION,
    ENV_DOMAIN,
    ENV_IAM_ACCOUNT,
    ENV_AUDIT_ACCOUNT,
    ENV_SECURITY_ACCOUNT,
    ENV_NETWORK_ACCOUNT,
    ENV_CORRELATION_ID,
    ENV_DOCUMENT_BUCKET_NAME,
    ENV_UI_BUCKET_NAME,
    ENV_CDK_DEFAULT_ACCOUNT,
    ENV_CDK_DEFAULT_REGION,
    ENV_CONSOLE,
    ENV_LOG_LEVEL,
    P_AUTOMATION_TYPE,
    P_AWS_PROFILE,
    P_AWS_REGION,
    P_TASKS,
    P_UNITS,
    P_CLIENT_NAME,
    P_CLIENT,
    P_CLIENT_REGION,
    P_SCOPE,
    P_PORTFOLIO,
    P_APP,
    P_BRANCH,
    P_BUILD,
    P_COMPONENT,
    P_ENVIRONMENT,
    P_BUCKET_NAME,
    P_BUCKET_REGION,
    P_INVOKER_ARN,
    P_INVOKER_NAME,
    P_INVOKER_REGION,
    P_API_LAMBDA_ARN,
    P_API_LAMBDA_NAME,
    P_API_HOST_URL,
    P_DYNAMODB_REGION,
    P_DYNAMODB_HOST,
    P_EXECUTE_LAMBDA_ARN,
    P_START_RUNNER_LAMBDA_ARN,
    P_DEPLOYSPEC_COMPILER_LAMBDA_ARN,
    P_COMPONENT_COMPILER_LAMBDA_ARN,
    P_REGION,
    P_AUTOMATION_ACCOUNT,
    P_ORGANIZATION_ACCOUNT,
    P_ORGANIZATION_EMAIL,
    P_ORGANIZATION_ID,
    P_ORGANIZATION_NAME,
    P_ARTEFACT_BUCKET_NAME,
    P_LOG_AS_JSON,
    P_VOLUME,
    P_LOG_DIR,
    P_DELIVERED_BY,
    P_LOCAL_MODE,
    P_USE_S3,
    P_ENFORCE_VALIDATION,
    P_DOMAIN,
    P_IAM_ACCOUNT,
    P_AUDIT_ACCOUNT,
    P_SECURITY_ACCOUNT,
    P_NETWORK_ACCOUNT,
    P_CORRELATION_ID,
    P_DOCUMENT_BUCKET_NAME,
    P_UI_BUCKET_NAME,
    P_CDK_DEFAULT_ACCOUNT,
    P_CDK_DEFAULT_REGION,
    P_CONSOLE,
    P_LOG_LEVEL,
    V_EMPTY,
)


# Map of environment variables to their property names.
# Properties are used on the command-line argument parser and other places like paramter names in functions.
# Not all Properties are included in this map.
argument_map: dict[str, str] = {
    P_AWS_PROFILE: ENV_AWS_PROFILE,
    P_AWS_REGION: ENV_AWS_REGION,
    P_TASKS: ENV_TASKS,
    P_UNITS: ENV_UNITS,
    P_AUTOMATION_TYPE: ENV_AUTOMATION_TYPE,
    P_CLIENT_NAME: ENV_CLIENT_NAME,
    P_CLIENT: ENV_CLIENT,
    P_CLIENT_REGION: ENV_CLIENT_REGION,
    P_SCOPE: ENV_SCOPE,
    P_PORTFOLIO: ENV_PORTFOLIO,
    P_APP: ENV_APP,
    P_BRANCH: ENV_BRANCH,
    P_BUILD: ENV_BUILD,
    P_COMPONENT: ENV_COMPONENT,
    P_ENVIRONMENT: ENV_ENVIRONMENT,
    P_BUCKET_NAME: ENV_BUCKET_NAME,
    P_BUCKET_REGION: ENV_BUCKET_REGION,
    P_INVOKER_ARN: ENV_INVOKER_LAMBDA_ARN,
    P_INVOKER_NAME: ENV_INVOKER_LAMBDA_NAME,
    P_INVOKER_REGION: ENV_INVOKER_LAMBDA_REGION,
    P_API_LAMBDA_ARN: ENV_API_LAMBDA_ARN,
    P_API_LAMBDA_NAME: ENV_API_LAMBDA_NAME,
    P_API_HOST_URL: ENV_API_HOST_URL,
    P_DYNAMODB_REGION: ENV_DYNAMODB_REGION,
    P_DYNAMODB_HOST: ENV_DYNAMODB_HOST,
    P_EXECUTE_LAMBDA_ARN: ENV_EXECUTE_LAMBDA_ARN,
    P_START_RUNNER_LAMBDA_ARN: ENV_START_RUNNER_LAMBDA_ARN,
    P_DEPLOYSPEC_COMPILER_LAMBDA_ARN: ENV_DEPLOYSPEC_COMPILER_LAMBDA_ARN,
    P_COMPONENT_COMPILER_LAMBDA_ARN: ENV_COMPONENT_COMPILER_LAMBDA_ARN,
    P_REGION: ENV_MASTER_REGION,
    P_DOMAIN: ENV_DOMAIN,
    P_IAM_ACCOUNT: ENV_IAM_ACCOUNT,
    P_AUDIT_ACCOUNT: ENV_AUDIT_ACCOUNT,
    P_SECURITY_ACCOUNT: ENV_SECURITY_ACCOUNT,
    P_NETWORK_ACCOUNT: ENV_NETWORK_ACCOUNT,
    P_AUTOMATION_ACCOUNT: ENV_AUTOMATION_ACCOUNT,
    P_ORGANIZATION_ACCOUNT: ENV_ORGANIZATION_ACCOUNT,
    P_ORGANIZATION_ID: ENV_ORGANIZATION_ID,
    P_ORGANIZATION_NAME: ENV_ORGANIZATION_NAME,
    P_ORGANIZATION_EMAIL: ENV_ORGANIZATION_EMAIL,
    P_ARTEFACT_BUCKET_NAME: ENV_ARTEFACT_BUCKET_NAME,
    P_LOG_AS_JSON: ENV_LOG_AS_JSON,
    P_VOLUME: ENV_VOLUME,
    P_LOG_DIR: ENV_LOG_DIR,
    P_DELIVERED_BY: ENV_DELIVERED_BY,
    P_LOCAL_MODE: ENV_LOCAL_MODE,
    P_USE_S3: ENV_USE_S3,
    P_ENFORCE_VALIDATION: ENV_ENFORCE_VALIDATION,
    P_CDK_DEFAULT_ACCOUNT: ENV_CDK_DEFAULT_ACCOUNT,
    P_CDK_DEFAULT_REGION: ENV_CDK_DEFAULT_REGION,
    P_CORRELATION_ID: ENV_CORRELATION_ID,
    P_DOCUMENT_BUCKET_NAME: ENV_DOCUMENT_BUCKET_NAME,
    P_UI_BUCKET_NAME: ENV_UI_BUCKET_NAME,
    P_CONSOLE: ENV_CONSOLE,
    P_LOG_LEVEL: ENV_LOG_LEVEL,
}

env_map: dict[str, str] = {
    ENV_AWS_PROFILE: P_AWS_PROFILE,
    ENV_AWS_REGION: P_AWS_REGION,
    ENV_TASKS: P_TASKS,
    ENV_UNITS: P_UNITS,
    ENV_AUTOMATION_TYPE: P_AUTOMATION_TYPE,
    ENV_CLIENT_NAME: P_CLIENT_NAME,
    ENV_CLIENT: P_CLIENT,
    ENV_CLIENT_REGION: P_CLIENT_REGION,
    ENV_SCOPE: P_SCOPE,
    ENV_PORTFOLIO: P_PORTFOLIO,
    ENV_APP: P_APP,
    ENV_BRANCH: P_BRANCH,
    ENV_BUILD: P_BUILD,
    ENV_COMPONENT: P_COMPONENT,
    ENV_ENVIRONMENT: P_ENVIRONMENT,
    ENV_BUCKET_NAME: P_BUCKET_NAME,
    ENV_BUCKET_REGION: P_BUCKET_REGION,
    ENV_INVOKER_LAMBDA_ARN: P_INVOKER_ARN,
    ENV_INVOKER_LAMBDA_NAME: P_INVOKER_NAME,
    ENV_INVOKER_LAMBDA_REGION: P_INVOKER_REGION,
    ENV_API_LAMBDA_ARN: P_API_LAMBDA_ARN,
    ENV_API_LAMBDA_NAME: P_API_LAMBDA_NAME,
    ENV_API_HOST_URL: P_API_HOST_URL,
    ENV_DYNAMODB_REGION: P_DYNAMODB_REGION,
    ENV_DYNAMODB_HOST: P_DYNAMODB_HOST,
    ENV_EXECUTE_LAMBDA_ARN: P_EXECUTE_LAMBDA_ARN,
    ENV_START_RUNNER_LAMBDA_ARN: P_START_RUNNER_LAMBDA_ARN,
    ENV_DEPLOYSPEC_COMPILER_LAMBDA_ARN: P_DEPLOYSPEC_COMPILER_LAMBDA_ARN,
    ENV_COMPONENT_COMPILER_LAMBDA_ARN: P_COMPONENT_COMPILER_LAMBDA_ARN,
    ENV_MASTER_REGION: P_REGION,
    ENV_DOMAIN: P_DOMAIN,
    ENV_IAM_ACCOUNT: P_IAM_ACCOUNT,
    ENV_AUDIT_ACCOUNT: P_AUDIT_ACCOUNT,
    ENV_SECURITY_ACCOUNT: P_SECURITY_ACCOUNT,
    ENV_NETWORK_ACCOUNT: P_NETWORK_ACCOUNT,
    ENV_AUTOMATION_ACCOUNT: P_AUTOMATION_ACCOUNT,
    ENV_ORGANIZATION_ACCOUNT: P_ORGANIZATION_ACCOUNT,
    ENV_ORGANIZATION_ID: P_ORGANIZATION_ID,
    ENV_ORGANIZATION_NAME: P_ORGANIZATION_NAME,
    ENV_ORGANIZATION_EMAIL: P_ORGANIZATION_EMAIL,
    ENV_ARTEFACT_BUCKET_NAME: P_ARTEFACT_BUCKET_NAME,
    ENV_LOG_AS_JSON: P_LOG_AS_JSON,
    ENV_VOLUME: P_VOLUME,
    ENV_LOG_DIR: P_LOG_DIR,
    ENV_DELIVERED_BY: P_DELIVERED_BY,
    ENV_LOCAL_MODE: P_LOCAL_MODE,
    ENV_USE_S3: P_USE_S3,
    ENV_ENFORCE_VALIDATION: P_ENFORCE_VALIDATION,
    ENV_CDK_DEFAULT_ACCOUNT: P_CDK_DEFAULT_ACCOUNT,
    ENV_CDK_DEFAULT_REGION: P_CDK_DEFAULT_REGION,
    ENV_CORRELATION_ID: P_CORRELATION_ID,
    ENV_DOCUMENT_BUCKET_NAME: P_DOCUMENT_BUCKET_NAME,
    ENV_UI_BUCKET_NAME: P_UI_BUCKET_NAME,
    ENV_CONSOLE: P_CONSOLE,
    ENV_LOG_LEVEL: P_LOG_LEVEL,
}


def get_environment(include_none: bool = False) -> dict[str, str]:
    """
    return a dictionary of automtion environment vriables

    If you want to include None values, set include_none to True.

    Returns:
        dict[str, str]: List of environment variables for core automation.
    """
    env_vars: dict[str, str] = {}
    for k in env_map.keys():
        if include_none or k in os.environ:
            env_vars[k] = os.getenv(k, "")
    return dict(sorted(env_vars.items()))


def set_environment_from_args(
    args: dict[str, str | None], *, ignore_none: bool = False, remove_none: bool = False
) -> None:
    """
    Set environment variables from specified P_ paramters from the command line.
    If you are calling after argparse, I highly recommend "ignore_none=True" as argparse sets ALL P_ paramtesr it
    sees even if you don't specify it on the command line.

    If you want to remove an environment variable, set the argement value to None and remove_none=True

    Args:
        args: The commadline paramters used to set enviroment variables.

    """
    for k, v in args.items():
        if v is None and ignore_none:
            continue
        env_key = env_map.get(k)
        if env_key:
            if v is None and remove_none:
                del os.environ[env_key]
            else:
                os.environ[env_key] = v if v else V_EMPTY


def get_arguments_from_env(
    env: dict | None = None, include_none: bool = False
) -> dict[str, str | None]:
    """
    Get the command line arguments from the environment variables.

    Args:
        include_none (bool, optional): Include None values in the dictionary. Defaults to None.

    Returns:
        dict[str, str]: The command line arguments.
    """
    if env is None:
        env = dict(os.environ)
    args: dict[str, str | None] = {}
    for k, v in env.items():
        arg_key = env_map.get(k)
        if arg_key and (v or include_none):
            args[arg_key] = v if v else None
    return dict(sorted(args.items()))


def args_to_env(arguments: dict[str, str | None]) -> dict[str, str]:
    """
    Convert the command line arguments to environment variables.

    Args:
        arguments (dict[str, str | None]): The command line arguments.

    Returns:
        dict[str, str]: The environment variables.
    """
    envs: dict[str, str] = {}
    for k, v in arguments.items():
        env_key = argument_map.get(k)
        if env_key:
            envs[env_key] = V_EMPTY if v is None else v
    return envs


def print_environmnt():

    # print all environment variables ins a table
    table = Table(title="Environment Variables", box=box.SQUARE)
    table.add_column("Environment Variable")
    table.add_column("Value")

    envs = get_environment(True)
    for key, value in envs.items():
        table.add_row(key, value)

    cprint(table)
    cprint()


def get_dotenv_config() -> dict[str, str | None]:
    """Use the dotenv library to load only the .env configuration and return it as a dictionary"""
    return dict(dotenv.dotenv_values())
