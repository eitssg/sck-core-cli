""" Manage and process client_vars.yaml """

from typing import Optional, Tuple, Dict
from .client_config import get_client_config_file


def get_client_vars(client: str) -> Dict:
    """Returns the found client vars or and empty dict"""
    return get_client_config_file(client, "client-vars.yaml")


def get_region_role(role: str = "automation", **kwargs) -> Tuple[Optional[str], str]:
    """Returns the found region and roleArn for the role name.  The region may be None
    For the role name, the default is 'automation'.  You can select:
        * automation
        * iam
        * organization
        * security
        * audit
    """
    account_number = kwargs.get(f"{role}_account", "")
    region_name = kwargs.get(f"{role}_region", kwargs.get("client_region", None))
    automation_role = kwargs.get("automation_role", "")
    return region_name, f"arn:aws:iam::{account_number}:role/{automation_role}"
