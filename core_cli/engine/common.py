import core_framework as util

from .._version import __version__

from ..common import (
    cprint,
    get_account_info,
    get_iam_user_name,
    check_admin_privileges,
    get_organization_info,
)


def exexecution_check(kwargs):
    """Print introduction to function and check for admin privileges

    Kwargs is mutated and the org_info and account_info are added to it.
    """

    cprint(f"Core Automation Organizations v{__version__}\n")

    user_name = get_iam_user_name()

    cprint(f"Welcome {user_name}!\n")

    aws_profile = util.get_aws_profile()

    cprint(f'You will be using AWS Profile: "{aws_profile}"\n')

    org_info = get_organization_info()

    kwargs["org_info"] = org_info

    cprint("Organization Information\n")

    organization_id = org_info["Id"]

    cprint(f"   Organization Name: {org_info['Name']}")
    cprint(f"   Organization ID  : {organization_id}")
    cprint(f"   Master Account   : {org_info['AccountId']}")
    cprint(f"   Master Email     : {org_info['Email']}")

    aws_account_id = kwargs["user"]["account"]
    account_info = get_account_info(aws_account_id)

    kwargs["account_info"] = account_info

    cprint("\nAccount Information\n")

    cprint(f"   Account Name     : {account_info['Name']}")
    cprint(f"   Account ID       : {account_info['Id']}")
    cprint(f"   Account Email    : {account_info['Email']}")

    if org_info["AccountId"] != account_info["Id"]:
        cprint(
            f"\nYou are not in the master account. You are in account {account_info['Name']}."
        )
        cprint("Please run this command from the master account.\n")
        cprint("Perhaps choose a different AWS_PROFILE.\n")
        cprint("Aborted")
        raise Exception("Not in master account")

    is_admin = check_admin_privileges(user_name)

    if not is_admin:
        cprint("\nYou do not have administrator privileges in this account.")
        cprint("Please run this command from an account with administrator privileges.")
        cprint("Perhaps choose a different AWS_PROFILE.\n")
        cprint("Aborted")
        raise Exception("Not an admin")

    cprint("\nCongratulations! We have checked and you are an admin!\n")
