import os
import boto3
from botocore.config import Config


def list_domains(**kwargs):
    # Create a Route 53 client
    http_proxy = os.environ["HTTP_PROXY"]
    https_proxy = os.environ["HTTPS_PROXY"]
    aws_profile = os.environ.get("AWS_PROFILE", None)
    aws_region = kwargs.get("aws_region", "ap-southeast-1")
    proxy_definition = {"http": http_proxy, "https": https_proxy}

    os.environ["http_proxy"] = http_proxy
    os.environ["https_proxy"] = https_proxy

    d = dict(os.environ)
    print(d)

    print(f"Client {aws_profile}")
    print(f"Region {aws_region}")
    print(proxy_definition)

    session = boto3.Session(profile_name=aws_profile)

    # Create a Route 53 client using the session
    config = Config(proxies=proxy_definition)
    client = session.client("route53domains", config=config)

    try:
        # Call the list_domains method to retrieve all registered domains
        response = client.list_domains()

        # Extract the domains from the response
        domains = response["Domains"]

        # Print the domains
        for domain in domains:
            print(domain["DomainName"])

    except Exception as e:
        print(f"An error occurred: {e}")


DOMAIN_TASKS = {"list": ("List the domains in the organization", list_domains)}


def add_domain_parser(subparsers):
    """Get the parser for the configuration command"""
    client = os.getenv("CLIENT", None)

    domain_parser = subparsers.add_parser(
        "domains",
        description="Manage the domains in the organization",
        usage="core domains [<task>] [--client <name>]",
        choices=DOMAIN_TASKS,
        help="Manage the domains in the organization",
    )
    domain_parser.set_group_title(0, "Configure actions")
    domain_parser.set_group_title(1, "Available options")

    domain_parser.add_argument(
        "task",
        choices=DOMAIN_TASKS.keys(),
        help=f"List all the domains in the organization",
    )
    domain_parser.add_argument(
        "-c",
        "--client",
        help=f"Client alias name of the organization. Default: {client}",
        required=client is None,
        default=client,
    )


def execute_domains(**kwargs):
    """Configure the client vars for the specified client."""
    task = kwargs.get("task", None)
    if task:
        DOMAIN_TASKS[task][1](**kwargs)
    else:
        print("Unknown task specified")
