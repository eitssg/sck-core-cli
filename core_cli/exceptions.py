class OrganizationNotSetException(Exception):
    def __init__(self):
        super().__init__(
            "Organization not set. Use 'core org' command line tools to setup the organization."
        )
