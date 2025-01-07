import os

import core_framework as util

from core_framework.constants import (
    ENV_TASKS,
    ENV_UNITS,
    ENV_AWS_PROFILE,
    ENV_AUTOMATION_TYPE,
    ENV_CLIENT_NAME,
    ENV_CLIENT,
    ENV_SCOPE,
    ENV_PORTFOLIO,
    ENV_APP,
    ENV_BRANCH,
    ENV_BUILD,
    ENV_BUCKET_NAME,
    ENV_BUCKET_REGION,
    ENV_INVOKER_LAMBDA_NAME,
    ENV_INVOKER_LAMBDA_REGION,
)


def get_environment(include_none: bool | None = None) -> dict[str, str]:
    """
    return a dictionary of automtion environment vriables

    If you

    Returns:
        dict[str, str]: List of environment variables for core automation.
    """
    env_vars = {
        ENV_AWS_PROFILE: util.get_aws_profile(),
        ENV_CLIENT: util.get_client(),
        ENV_PORTFOLIO: os.getenv(ENV_PORTFOLIO, None),
        ENV_APP: os.getenv(ENV_APP, None),
        ENV_BRANCH: os.getenv(ENV_BRANCH, None),
        ENV_BUILD: os.getenv(ENV_BUILD, None),
        ENV_TASKS: os.getenv(ENV_TASKS, None),
        ENV_UNITS: os.getenv(ENV_UNITS, None),
        ENV_SCOPE: util.get_automation_scope(),
        ENV_AUTOMATION_TYPE: os.getenv(ENV_AUTOMATION_TYPE, None),
        ENV_CLIENT_NAME: util.get_client_name(),
        ENV_BUCKET_NAME: util.get_bucket_name(),
        ENV_BUCKET_REGION: util.get_bucket_region(),
        ENV_INVOKER_LAMBDA_NAME: util.get_invoker_lambda_name(),
        ENV_INVOKER_LAMBDA_REGION: util.get_invoker_lambda_region(),
    }

    return {k: v or "" for k, v in env_vars.items() if include_none or v}


def set_environment(**kwargs):  # noqa: C901
    """
    Set environment variables from specified paramters from the command line.

    Args:
        **kwargs: The commadline paramters used to set enviroment variables.

    """
    if "tasks" in kwargs:
        os.environ[ENV_TASKS] = kwargs.get("tasks")
    if "units" in kwargs:
        os.environ[ENV_UNITS] = kwargs.get("units")
    if "aws_profile" in kwargs:
        os.environ[ENV_AWS_PROFILE] = kwargs.get("aws_profile")
    if "automation_type" in kwargs:
        os.environ[ENV_AUTOMATION_TYPE] = kwargs.get("automation_type")
    if "client_name" in kwargs:
        os.environ[ENV_CLIENT_NAME] = kwargs.get("client_name")
    if "client" in kwargs:
        os.environ[ENV_CLIENT] = kwargs.get("client")
    if "scope" in kwargs:
        os.environ[ENV_SCOPE] = kwargs.get("scope")
    if "portfolio" in kwargs:
        os.environ[ENV_PORTFOLIO] = kwargs.get("portfolio")
    if "app" in kwargs:
        os.environ[ENV_APP] = kwargs.get("app")
    if "branch" in kwargs:
        os.environ[ENV_BRANCH] = kwargs.get("branch")
    if "build" in kwargs:
        os.environ[ENV_BUILD] = kwargs.get("build")
    if "bucket_name" in kwargs:
        os.environ[ENV_BUCKET_NAME] = kwargs.get("bucket_name")
    if "bucket_region" in kwargs:
        os.environ[ENV_BUCKET_REGION] = kwargs.get("bucket_region")
    if "invoker_lambda_name" in kwargs:
        os.environ[ENV_INVOKER_LAMBDA_NAME] = kwargs.get("invoker_lambda_name")
    if "invoker_lambda_region" in kwargs:
        os.environ[ENV_INVOKER_LAMBDA_REGION] = kwargs.get("invoker_lambda_region")
