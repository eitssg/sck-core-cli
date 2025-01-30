import json

from rich import box
from rich.table import Table

import core_helper.aws as aws

from ..console import get_account_info, get_input, cprint, jprint

from ..cmdparser.cmdparser import ExecuteCommandsType

from .common import exexecution_check


def detach_policy_from_account(policy_id: str, account_id: str):
    """Detach the policy from the account"""
    cprint(f"\nDetaching policy {policy_id} from account: {account_id}")
    org_client = aws.org_client()
    org_client.detach_policy(PolicyId=policy_id, TargetId=account_id)


def detach_policy_from_ou(policy_id: str, ou_id: str):
    """Detach the policy from the OU"""
    cprint(f"\nDetaching policy {policy_id} from OU: {ou_id}")
    org_client = aws.org_client()
    org_client.detach_policy(PolicyId=policy_id, TargetId=ou_id)


def attach_policy_to_account(policy_id: str, account_id: str):
    """Attach the policy to the account"""
    cprint(f"\nAttaching policy {policy_id} to account: {account_id}")
    org_client = aws.org_client()
    org_client.attach_policy(PolicyId=policy_id, TargetId=account_id)


def attach_policy_to_ou(policy_id: str, ou_id: str):
    """Attach the policy to the OU"""
    cprint(f"\nAttaching policy {policy_id} to OU: {ou_id}")
    org_client = aws.org_client()
    org_client.attach_policy(PolicyId=policy_id, TargetId=ou_id)


def get_ou_info(ou_id):
    """Get the organizational unit information."""
    org_client = aws.org_client()
    response = org_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
    return response["OrganizationalUnit"]


def print_policy_information(policy_id: str, file_prefix: str | None = None):
    """Retrieve and print the policy information by policy_id."""

    org_client = aws.org_client()
    response = org_client.describe_policy(PolicyId=policy_id)

    policy = response["Policy"]
    policy_name = policy["PolicySummary"]["Name"]
    policy_description = policy["PolicySummary"]["Description"]
    policy_content = json.loads(policy["Content"])

    cprint(f"Policy ID   : {policy_id}", style="bold red")
    cprint(f"Policy      : {policy_name}", style="bold red")
    cprint(f"Description : {policy_description}", style="bold red")

    cprint("")

    if file_prefix:
        filename = f"{file_prefix}_{policy_name.lower()}.json"
        with open(filename, "w") as f:
            json.dump(policy_content, f, indent=2)
        cprint(f"SCP policy saved to {filename}", style="bold green")
    else:
        jprint(json.dumps(policy_content, indent=2))

    # Print targets in a table with the columns Type, TargetId, Name
    table = Table(title="Policy Attachments", box=box.SQUARE)
    table.add_column("Type", style="green")
    table.add_column("TargetId")
    table.add_column("Name")

    targets = org_client.list_targets_for_policy(PolicyId=policy_id)["Targets"]
    for target in targets:
        table.add_row(target["Type"], target["TargetId"], target["Name"])

    cprint(table)


def list_all_scp_policies(file_prefix: str | None = None):
    """Get the service control policies attached to the organization and print them in JSON format."""
    org_client = aws.org_client()
    paginator = org_client.get_paginator("list_policies")
    response_iterator = paginator.paginate(Filter="SERVICE_CONTROL_POLICY")

    for response in response_iterator:
        for policy in response["Policies"]:
            print_policy_information(policy["Id"], file_prefix)
            cprint("")


def add_common_parameters(parser):
    """Add the common parameters to the parser"""

    parser.add_argument(
        "-r",
        "--automation-role",
        default="core-automation-role",
        help="Role name",
        required=False,
    )


def add_common_policy_parameters(parser, help):

    add_common_parameters(parser)

    parser.add_argument(
        "-p",
        "--policy-id",
        required=True,
        help=help,
    )


TASKS: ExecuteCommandsType = {}


def get_scp_tasks(subparser) -> ExecuteCommandsType:
    """Add the SCP tasks to the subparser"""

    scp_parser = subparser.add_parser(
        "scp",
        description="Manage the SCP policies",
        usage="core organization scp <task> [<args>]",
        help="Manage the SCP policies",
    )
    scp_parser.set_group_title(0, "SCP tasks")
    scp_parser.set_group_title(1, "Available options")

    task_parsers = scp_parser.add_custom_subparsers(dest="task", metavar="<task>")

    TASKS.update(get_scp_list_task(task_parsers))
    TASKS.update(get_scp_show_task(task_parsers))
    TASKS.update(get_scp_attach_task(task_parsers))
    TASKS.update(get_scp_detach_task(task_parsers))
    TASKS.update(get_scp_create_task(task_parsers))
    TASKS.update(get_scp_delete_task(task_parsers))

    return {"scp": (scp_parser.description, execute_organization)}


def execute_organization(**kwargs):
    """Execute the organization tasks"""
    task = kwargs.get("task")
    if task in TASKS:
        TASKS[task][1](**kwargs)
    else:
        print(f"Task {task} not found")


def get_scp_show_task(subparsers) -> ExecuteCommandsType:
    """Add the show parser"""

    description = "Show/Describe an SCP policy"
    show_parser = subparsers.add_parser(
        "show",
        description=description,
        usage="core organization scp list [<options>]",
        help=description,
    )
    show_parser.set_group_title(0, "Show policy actions")
    show_parser.set_group_title(1, "Available options")

    show_parser.add_argument(
        "-p",
        "--policy-id",
        dest="policy_id",
        metavar="<policy_id>",
        required=True,
        help="Policy id to show",
    )

    return {"show": (description, execute_show)}


def get_scp_list_task(subparsers) -> ExecuteCommandsType:
    """Add the list parser"""

    description = "List the SCP policies"
    list_parser = subparsers.add_parser(
        "list",
        description=description,
        usage="core organization scp list [<options>]",
        help=description,
    )
    list_parser.set_group_title(0, "List actions")
    list_parser.set_group_title(1, "Available options")

    list_parser.add_argument(
        "--out",
        help="File prefix to save the SCP policies",
    )

    return {"list": (description, execute_list)}


def execute_show(**kwargs):
    """Run the SCP show process"""

    exexecution_check(kwargs)

    policy_id = kwargs.get("policy_id")

    cprint("Service Control Policy (SCP):\n")

    print_policy_information(policy_id)

    cprint("")
    cprint("Done.")


def execute_list(**kwargs):
    """List the SCP policies"""

    exexecution_check(kwargs)

    cprint("Listing Service Control Policy (SCP):\n")

    output_file = kwargs.get("out")
    list_all_scp_policies(output_file)

    cprint("Done")


def get_scp_attach_task(subparsers) -> ExecuteCommandsType:
    """Add the attach parser"""

    description = "Attach the SCP policy"
    attach_parser = subparsers.add_parser(
        "attach",
        description=description,
        usage="core organization scp attach [<options>]",
        help=description,
    )
    attach_parser.set_group_title(0, "Attach actions")
    attach_parser.set_group_title(1, "Available options")

    attach_parser.add_argument(
        "-p",
        "--policy-id",
        dest="policy_id",
        metavar="<policy-id>",
        required=True,
        help="Policy id to show",
    )

    attach_parser.add_argument(
        "-t",
        "--target-id",
        dest="target_id",
        metavar="<target-id>",
        required=False,
        help="Account ID or OU ID to attach the policy to",
    )

    return {"attach": (description, execute_attach)}


def execute_attach(**kwargs):
    """Run the SCP attach process"""

    exexecution_check(kwargs)

    target_id = kwargs.get("target_id")

    if not target_id:
        cprint(
            "You must specify either an account or an OU to attach the policy to with the --target-id option.\n",
            style="bold red",
        )
        return

    policy_id = kwargs.get("policy_id")

    cprint("Service Control Policy (SCP):\n")

    print_policy_information(policy_id)

    if target_id.startswith("ou-"):
        show_ou_info(target_id)
    else:
        show_account_info(target_id)

    cprint("")

    result = get_input("Do you want to attach this policy?", ["yes", "no"])
    if result == "no":
        cprint("\nAborted", style="bold red")
        return

    if target_id.startswith("ou-"):
        attach_policy_to_ou(policy_id, target_id)
    else:
        attach_policy_to_account(policy_id, target_id)

    cprint("")
    cprint("Done")


def show_ou_info(ou_id: str):

    cprint("\nTarget Organizational Unit:")

    ou_info = get_ou_info(ou_id)

    cprint(f"   OU Name          : {ou_info['Name']}")
    cprint(f"   OU ID            : {ou_info['Id']}")


def show_account_info(account_id: str):

    cprint("\nTarget Account:")

    account_info = get_account_info(account_id)

    cprint(f"   Account Name     : {account_info['Name']}")
    cprint(f"   Account ID       : {account_info['Id']}")
    cprint(f"   Account Email    : {account_info['Email']}")


def get_scp_detach_task(subparsers) -> ExecuteCommandsType:
    """Add the detach parser"""

    description = "Detach the SCP policy"
    detach_parser = subparsers.add_parser(
        "detach",
        description=description,
        usage="core organization scp detach [<options>]",
        help=description,
    )
    detach_parser.set_group_title(0, "Detach actions")
    detach_parser.set_group_title(1, "Available options")

    detach_parser.add_argument(
        "-p",
        "--policy-id",
        dest="policy_id",
        metavar="<policy-id>",
        required=True,
        help="Policy id to detatch from a target",
    )

    detach_parser.add_argument(
        "-t",
        "--target-id",
        dest="target_id",
        metavar="<target-id>",
        required=False,
        help="Account ID or OU ID to detach the policy from",
    )

    return {"detach": (description, execute_detach)}


def execute_detach(**kwargs):
    """detach a poicy from an account or OU"""

    exexecution_check(kwargs)

    target_id = kwargs.get("target_id")

    if not target_id:
        cprint(
            "You must specify either an account or an OU to detach the policy from with the --target-id option.\n",
            style="bold red",
        )
        return

    policy_id = kwargs.get("policy_id")

    cprint("Service Control Policy (SCP):\n")

    print_policy_information(policy_id)

    if target_id.startswith("ou-"):
        show_ou_info(target_id)
    else:
        show_account_info(target_id)

    cprint("")

    result = get_input("Do you want to detach this policy?", ["yes", "no"])
    if result == "no":
        cprint("\nAborted", style="bold red")
        return

    if target_id.startswith("ou-"):
        detach_policy_from_ou(policy_id, target_id)
    else:
        detach_policy_from_account(policy_id, target_id)

    cprint("")
    cprint("Done")


def get_scp_create_task(subparsers) -> ExecuteCommandsType:
    """Add the create parser"""

    description = "Create the SCP policy"
    create_parser = subparsers.add_parser(
        "create",
        description=description,
        usage="core organization scp create [<options>]",
        help=description,
    )
    create_parser.set_group_title(0, "Create actions")
    create_parser.set_group_title(1, "Available options")

    add_common_policy_parameters(create_parser, "Policy id to create")

    return {"create": (description, execute_create)}


def execute_create(**kwargs):
    print("Create SCP Policy")
    print(kwargs)


def get_scp_delete_task(subparsers) -> ExecuteCommandsType:
    """Add the delete parser"""

    description = "Delete the SCP policy"
    delete_parser = subparsers.add_parser(
        "delete",
        description=description,
        usage="core organization scp delete [<options>]",
        help=description,
    )
    delete_parser.set_group_title(0, "Delete actions")
    delete_parser.set_group_title(1, "Available options")

    add_common_policy_parameters(delete_parser, "Policy id to delete")

    return {"delete": (description, execute_delete)}


def execute_delete(**kwargs):
    print("Delete SCP Policy")
    print(kwargs)
