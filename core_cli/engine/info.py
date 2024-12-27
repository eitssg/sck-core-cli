def execute_info(args):
    pass


def add_info_parser(subparsers):
    """Add the info parser to the subparsers"""

    info_parser = subparsers.add_parser(
        "info",
        description="Show information about the engine",
        usage="core engine info",
        help="Show information about the engine",
    )

    return {"info": (info_parser.description, execute_info)}
