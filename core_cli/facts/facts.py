import core_framework as util

from core_framework.constants import P_CLIENT, P_PRN

from core_cli.cmdparser import ExecuteCommandsType
from core_cli.apiclient import APIClient
from core_cli.console import cprint, jprint


def get_facts(data: dict) -> dict:

    client = data.get(P_CLIENT)
    prn = data.get(P_PRN)

    api_client = APIClient.get_instance()
    headers = api_client.get_headers(data)

    params = {"prn": prn}

    result = api_client.get(f"/api/v1/facts/{client}", params=params, headers=headers)
    if result.status_code == 200:
        return result.json()
    error_json = result.json()
    return {"error": error_json["data"]["message"]}


def get_facts_command(parser) -> ExecuteCommandsType:
    """add the facts parser"""
    description = "Retrieve context or FACTS database of a deployment"
    facts_parser = parser.add_parser(
        "facts",
        description=description,
        help=description,
    )

    facts_parser.set_group_title(0, "Available Facts Actions")
    facts_parser.set_group_title(1, "Available Facts Options")

    facts_parser.add_argument(
        "--prn",
        dest=P_PRN,
        metavar="<prn>",
        help="The prn to retrieve. ex. --prn prn:customers:api:master:v1.0",
        required=True,
    )

    return {"facts": (description, execute_facts)}


def execute_facts(**kwargs):

    prn = kwargs.get(P_PRN)
    cprint("Retrieving FACTS data...\n", style="bold")
    cprint(f"PRN: {prn}")

    data = get_facts(kwargs)
    jprint(util.to_json(data))
