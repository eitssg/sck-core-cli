import os
from rich.table import Table
from rich import box

from .common import cprint

from core_framework.constants import (
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
    ENV_DYNAMODB_REGION,
    ENV_DYNAMODB_HOST,
    ENV_EXECUTE_LAMBDA_ARN,
    ENV_START_RUNNER_LAMBDA_ARN,
    ENV_DEPLOYSPEC_COMPILER_LAMBDA_ARN,
    ENV_COMPONENT_COMPILER_LAMBDA_ARN,
    ENV_RUNNER_STEP_FUNCTION_ARN,
    ENV_MASTER_REGION,
    ENV_AUTOMATION_ACCOUNT,
    ENV_ARTEFACT_BUCKET_NAME,
    ENV_LOG_AS_JSON,
    ENV_VOLUME,
    ENV_LOG_DIR,
    ENV_DELIVERED_BY,
    ENV_LOCAL_MODE,
    ENV_USE_S3,
    ENV_ENFORCE_VALIDATION,
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
    P_INVOKER_LAMBDA_ARN,
    P_INVOKER_LAMBDA_NAME,
    P_INVOKER_LAMBDA_REGION,
    P_API_LAMBDA_ARN,
    P_API_LAMBDA_NAME,
    P_DYNAMODB_REGION,
    P_DYNAMODB_HOST,
    P_EXECUTE_LAMBDA_ARN,
    P_START_RUNNER_LAMBDA_ARN,
    P_DEPLOYSPEC_COMPILER_LAMBDA_ARN,
    P_COMPONENT_COMPILER_LAMBDA_ARN,
    P_RUNNER_STEP_FUNCTION_ARN,
    P_REGION,
    P_AUTOMATION_ACCOUNT,
    P_ARTEFACT_BUCKET_NAME,
    P_LOG_AS_JSON,
    P_VOLUME,
    P_LOG_DIR,
    P_DELIVERED_BY,
    P_LOCAL_MODE,
    P_USE_S3,
    P_ENFORCE_VALIDATION,
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
    P_INVOKER_LAMBDA_ARN: ENV_INVOKER_LAMBDA_ARN,
    P_INVOKER_LAMBDA_NAME: ENV_INVOKER_LAMBDA_NAME,
    P_INVOKER_LAMBDA_REGION: ENV_INVOKER_LAMBDA_REGION,
    P_API_LAMBDA_ARN: ENV_API_LAMBDA_ARN,
    P_API_LAMBDA_NAME: ENV_API_LAMBDA_NAME,
    P_DYNAMODB_REGION: ENV_DYNAMODB_REGION,
    P_DYNAMODB_HOST: ENV_DYNAMODB_HOST,
    P_EXECUTE_LAMBDA_ARN: ENV_EXECUTE_LAMBDA_ARN,
    P_START_RUNNER_LAMBDA_ARN: ENV_START_RUNNER_LAMBDA_ARN,
    P_DEPLOYSPEC_COMPILER_LAMBDA_ARN: ENV_DEPLOYSPEC_COMPILER_LAMBDA_ARN,
    P_COMPONENT_COMPILER_LAMBDA_ARN: ENV_COMPONENT_COMPILER_LAMBDA_ARN,
    P_RUNNER_STEP_FUNCTION_ARN: ENV_RUNNER_STEP_FUNCTION_ARN,
    P_REGION: ENV_MASTER_REGION,
    P_AUTOMATION_ACCOUNT: ENV_AUTOMATION_ACCOUNT,
    P_ARTEFACT_BUCKET_NAME: ENV_ARTEFACT_BUCKET_NAME,
    P_LOG_AS_JSON: ENV_LOG_AS_JSON,
    P_VOLUME: ENV_VOLUME,
    P_LOG_DIR: ENV_LOG_DIR,
    P_DELIVERED_BY: ENV_DELIVERED_BY,
    P_LOCAL_MODE: ENV_LOCAL_MODE,
    P_USE_S3: ENV_USE_S3,
    P_ENFORCE_VALIDATION: ENV_ENFORCE_VALIDATION,
}


def get_environment(include_none: bool | None = None) -> dict[str, str]:
    """
    return a dictionary of automtion environment vriables

    If you want to include None values, set include_none to True.

    Returns:
        dict[str, str]: List of environment variables for core automation.
    """
    env_vars: dict[str, str] = {}
    for v in argument_map.values():
        if include_none or v in os.environ:
            env_vars[v] = os.getenv(v, "")
    return env_vars


def set_environment(**kwargs):
    """
    Set environment variables from specified paramters from the command line.

    Args:
        **kwargs: The commadline paramters used to set enviroment variables.

    """
    for k, v in argument_map.items():
        if k in kwargs:
            os.environ[v] = kwargs.get(k)


def print_environmnt():

    # print all environment variables ins a table
    table = Table(title="Environment Variables", box=box.SQUARE)
    table.add_column("Environment Variable")
    table.add_column("Value")

    envs = get_environment()
    for key, value in envs.items():
        table.add_row(key, value)

    cprint(table)
    cprint()
