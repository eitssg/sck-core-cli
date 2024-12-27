""" check if all VPCs are in the account_registry """

import os
import yaml

account_registry: dict = {}


def cf(fn):
    """return the file name from the location of the config folder"""
    FOLDER = os.path.join("..", "..", "core-config")
    return os.path.join(FOLDER, fn)


def get_registry():
    """return the account registry"""
    global account_registry  # pylint: disable=global-statement

    if len(account_registry) == 0:
        with open(cf("account-registry.yaml"), "r", encoding="utf-8") as f:
            account_registry = yaml.safe_load(f)
    return account_registry


def locate_account_name(check_name: str) -> bool:
    """return true if the account name is found in the account_registry"""
    ar = get_registry()
    portfolios = ar["portfolios"]
    for portfilio in portfolios:
        zones = portfilio.get("zones", [])
        for zone in zones:
            zone_name = zone.get("name")
            alias = zone.get("alias")
            if (zone_name and zone_name == check_name) or (
                alias and alias == check_name
            ):
                return True
    return False


print("Checking to see if account names are in the account registry")

DELTE_VPC_FILES = [
    cf("delete-default-vpcs.yaml"),
    cf("delete-default-vpcs1.yaml"),
    cf("hosted-zones-nonprod.yaml"),
    cf("hosted-zones-prod.yaml"),
    cf("hosted-zones.yaml"),
]
for file in DELTE_VPC_FILES:
    print(f"Checking {file}")
    with open(file, "r", encoding="utf-8") as f:
        vpcs = yaml.safe_load(f)
        for name in vpcs["accounts"]:
            FOUND = locate_account_name(name)
            if not FOUND:
                print(f"VPC {name} not found in account-registry.yaml")
