def add_migrate_parser(subparsers, description):
    """add the source parser"""

    description = "API DB migration"

    subparser = subparsers.add_parser(
        "migrate",
        usage="core engine migrate [<options>]",
        description=description,
        help=description,
    )
    subparser.set_group_title(0, "Migrate tasks")
    subparser.set_group_title(1, "Available options")

    return {"migrate": (description, execute_migrate)}


def execute_migrate(**kwargs):
    """execute the command"""
    print("Migrate")
