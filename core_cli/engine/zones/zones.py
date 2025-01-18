""" CLI for managing zones """

from ...cmdparser import ExecuteCommandsType

from .associate import associate_zones


def action_verify(**kwargs):
    """verify the zones"""
    print(f"Verify: {dict(kwargs)}")


ACTIONS: ExecuteCommandsType = {
    "associate": (
        "Ensure all zones are registered as private zones in Route53",
        associate_zones,
    ),
    "verify": ("Verify all zones and print any anomolies", action_verify),
}


def add_zones_parser(subparsers) -> ExecuteCommandsType:
    """add the clean parser"""

    description = "List Landing Zones / accounts / fact"

    zones_parser = subparsers.add_parser(
        "zones",
        description=description,
        choices=ACTIONS,
        help=description,
    )
    zones_parser.set_group_title(0, "Zone actions")
    zones_parser.set_group_title(1, "Avalable options")

    zones_parser.add_argument("action", choices=ACTIONS.keys())

    zones_parser.add_argument(
        "-b",
        "--branch",
        help="Branch name to use for the configuration file\n"
        "Examples:  dev, nonprod, or prod. Defaults to 'None'",
    )

    return {"zones": (description, execute_zones)}


def execute_zones(**kwargs):
    """execute the command"""
    action = kwargs.get("action")
    any(action and ACTIONS[action][1](**kwargs) or print("No action specified"))
