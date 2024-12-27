""" Module that will make sure that privete zones are associated with all zones in the account_registry """

from typing import Any, Dict
import botocore
import boto3
from ...configure import get_client_config_file

_r53_client: Dict[str, Any] = {}


def _assume_role(profile, account, role_name, region):
    """assume the role"""
    try:
        client = boto3.client("sts", profile=profile, region_name=region)
        response = client.assume_role(
            RoleArn=f"arn:aws:iam::{account}:role/{role_name}"
        )
        if response:
            return boto3.session.Session(
                aws_access_key_id=response["Credentials"]["AccessKeyId"],
                aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
                aws_session_token=response["Credentials"]["SessionToken"],
                region_name=region,
            )
    except botocore.exceptions.ClientError as e:
        print(f"Failed to assume role: {e}")
        print(
            "If you have not create the appriate automation roles, please run the following command: \n\n"
        )
        print("$ core engine init roles --client <client>\n")
        return None


def _get_r53_client(profile_name, account, role_name, region):
    """get the r53 client singletone"""
    try:
        if _r53_client.get(account) is None:
            session = _assume_role(profile_name, account, role_name, region)
            _r53_client[account] = session.client("route53")
        return _r53_client[account]
    except botocore.exceptions.ClientError as e:
        raise OSError("Failed to get R53 client") from e


def _process_services_vpc(**kwargs):

    client_account = kwargs["account"]
    client_region = kwargs["client_region"]

    profile = kwargs.get("aws_profile")

    hosted_zone_id = kwargs["hosted_zone"]["Id"]
    hosted_zone_name = kwargs["hosted_zone"]["Name"]

    # Get all the hosted zones in the client account
    hosted_zone = _get_r53_client(
        profile, client_account, role, client_region
    ).get_hosted_zone(Id=hosted_zone_id)

    role = kwargs.get("automation-role", "AutomationEngineAccess")

    services_account = kwargs["services_vpc"]["account"]
    services_vpc_id = kwargs["services_vpc"]["vpc_id"]
    services_region = kwargs["services_vpc"]["region"]

    print(
        f"== Associating ({client_account}) => ({hosted_zone_name}|{services_vpc_id}|{services_region})"
    )

    if any(
        (vpc["VPCId"] == services_vpc_id and vpc["VPCRegion"] == services_region)
        for vpc in hosted_zone.get("VPCs", [])
    ):
        print("Hosted zone already associated with VPC, skipping")
        return

    try:
        if services_account != client_account:
            print("Creating association authorization")
            _get_r53_client(
                profile, services_account, role, services_region
            ).create_vpc_association_authorization(
                HostedZoneId=hosted_zone_id,
                VPC={"VPCRegion": services_region, "VPCId": services_vpc_id},
            )

        print("Associating zone to VPC")
        _get_r53_client(
            profile, client_account, role, client_region
        ).associate_vpc_with_hosted_zone(
            HostedZoneId=hosted_zone_id,
            VPC={"VPCRegion": services_region, "VPCId": services_vpc_id},
        )

    except botocore.exceptions.ClientError as e:
        # translate from client error to value error
        raise ValueError("Failed to associate zone with VPC") from e


def _process_zone(**kwargs):
    """process the zone and associate to service vpc(s)"""
    account = kwargs["account"]
    hosted_zone_id = kwargs["hosted_zone"]["Id"]
    try:
        hosted_zone = _r53_client[account].get_hosted_zone(Id=hosted_zone_id)
    except botocore.exceptions.ClientError as e:
        # translate from client error to value error
        raise ValueError("Failed to get hosted zone") from e

    # Associate hosted zone with services VPCs
    services_vpcs = kwargs["client_vars"]["services_vpcs"]
    for services_vpc in services_vpcs:
        _process_services_vpc(
            **kwargs, services_vpc=services_vpc, hosted_zone=hosted_zone
        )


def _process_account(**kwargs):
    """we will process all zones in the current account that have a suffix specified in the hosted-zones.yaml file"""
    zone_suffix = kwargs["client_vars"]["zone_suffix"]
    profile_name = kwargs["aws_profile"]
    administator_role = kwargs.get("automation-role", "AutomationEngineAccess")
    region = kwargs["client_region"]
    account = kwargs["account"]

    try:
        response = _get_r53_client(
            profile_name, account, administator_role, region
        ).list_hosted_zones()
    except botocore.exceptions.ClientError as e:
        # """ translate ClientError to ValueError """
        raise ValueError("Failed to list hosted zones") from e

    # Filter hosted zones to find our one
    hosted_zone_list = []
    for hosted_zone in response["HostedZones"]:
        if hosted_zone["Name"].endswith(zone_suffix):
            hosted_zone_list.append(hosted_zone)
    if not hosted_zone_list:
        raise ValueError(f"Could not find hosted zone for {account}")

    # process all sonzes in with the zone_suffix
    for hosted_zone in hosted_zone_list:
        _process_zone(**kwargs, hosted_zone=hosted_zone)


def _process_client_vars(**kwargs):
    accounts = kwargs["client_vars"]["accounts"]
    for account in accounts:
        _process_account(**kwargs, account=account)


def associate_zones(**kwargs):
    """associate the zones in the requested branch"""
    client = kwargs.get("client")
    if not client:
        raise ValueError("Client is required")

    print(f"Associating hosted-zones for client: {client}")
    branch = kwargs.get("branch")
    if branch is None:
        branch = ""
    print(f"You have elected to process zones in branch: '{branch}'")

    if len(branch) > 0:
        branch = f"-{branch}"
    filename = f"hosted-zones{branch}.yaml"

    client_vars = get_client_config_file(client, filename)
    if len(client_vars) == 0:
        raise ValueError(f"Could not load '{filename}' for client '{client}'")

    _process_client_vars(**kwargs, client_vars=client_vars)
