import core_helper.aws as aws


from .common import exexecution_check


def get_root_id():
    """Get the root ID of the organization."""
    org_client = aws.org_client()
    response = org_client.list_roots()
    roots = response["Roots"]
    root_id = roots[0]["Id"]
    return root_id


def get_ou_info(ou_id):
    """Get the organizational unit information."""
    org_client = aws.org_client()
    response = org_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
    return response["OrganizationalUnit"]


def list_organizational_units(parent_id):
    """List all organizational units for a given parent ID."""

    org_client = aws.org_client()
    paginator = org_client.get_paginator("list_organizational_units_for_parent")
    response_iterator = paginator.paginate(ParentId=parent_id)

    ous = []
    for response in response_iterator:
        ous.extend(response["OrganizationalUnits"])

    return ous


def get_child_accounts(parent_id):
    """Get the child accounts array"""

    org_client = aws.org_client()
    paginator = org_client.get_paginator("list_accounts_for_parent")
    response_iterator = paginator.paginate(ParentId=parent_id)

    accounts = []
    for response in response_iterator:
        for account in response["Accounts"]:
            account_id = account["Id"]
            account_name = account["Name"]
            account_email = account["Email"]
            accounts.append((account_id, account_name, account_email))

    return accounts


def print_organizational_units_tree(parent_id: str, level: int = 0):
    """Print the organizational units and accounts tree structure incrementally."""
    indent = "|   " * level
    if level == 0:
        print(f"|-- Root (ID: {parent_id})")
    else:
        ou_info = get_ou_info(parent_id)
        print(f"{indent}|-- {ou_info['Name']} (ID: {ou_info['Id']})")

    accounts = get_child_accounts(parent_id)
    for account in accounts:
        print(
            f"{indent}|   |-- Account: {account[1]} (ID: {account[0]}, Email: {account[2]})"
        )

    ous = list_organizational_units(parent_id)
    for ou in ous:
        print_organizational_units_tree(ou["Id"], level + 1)


def get_show_tasks(subparsers):
    """Add the show parser"""

    description = "Show organization accounts"
    show_parser = subparsers.add_parser(
        "show",
        description=description,
        usage="core organization show [<options>]",
        help=description,
    )
    show_parser.set_group_title(0, "Show actions")
    show_parser.set_group_title(1, "Available options")

    return {"show": (description, execute_show)}


def execute_show(**kwargs):

    exexecution_check(kwargs)

    print("Organizational Units Tree:\n")

    root_id = get_root_id()

    print_organizational_units_tree(root_id)

    print("")
    print("Done")
