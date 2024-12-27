""" Operat the CLI for initialzing the core platform """

import json
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


def create_trust_policy(iam, role_name, resources_dir):
    """create the trust policy on the provided role"""
    # Initialize Jinja2 environment
    env = Environment(loader=FileSystemLoader(resources_dir))

    if not os.path.isfile(os.path.join(resources_dir, "trust-policy.json.j2")):
        raise ValueError(f"Trust policy template not found in {resources_dir}")

    # Load and render the trust policy template
    trust_template_name = "trust-policy.json.j2"
    try:
        trust_template = env.get_template(trust_template_name)
    except TemplateNotFound as e:
        raise FileNotFoundError(
            f"Template '{trust_template_name}' not found in '{resources_dir}'"
        ) from e

    trust_policy_document = trust_template.render(service="ec2.amazonaws.com")

    # Check if the role already exists
    try:
        iam.get_role(RoleName=role_name)
        print(f"Role '{role_name}' already exists. Updating trust policy.")
        # Update the trust policy
        iam.update_assume_role_policy(
            RoleName=role_name, PolicyDocument=trust_policy_document
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            # Role does not exist, so create it
            try:
                iam.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=trust_policy_document,
                    Description="Role with full access to CloudFormation, Route53, S3, SecretsManager, and KMS",
                )
                print(f"Role '{role_name}' created.")
            except ClientError as e1:
                raise OSError(
                    f"An AWS error occurred while creating the role: {e1.response['Error']['Message']}"
                ) from e1
        else:
            # Raise any other ClientError
            raise OSError(
                f"An AWS error occurred: {e.response['Error']['Message']}"
            ) from e


def create_access_policy(iam, session, role_name, resources_dir):
    """crate the access policy for the role"""
    # Initialize Jinja2 environment
    env = Environment(loader=FileSystemLoader(resources_dir))

    # Load and render the access policy template
    access_template_name = "access-policy.json.j2"
    try:
        access_template = env.get_template(access_template_name)
    except TemplateNotFound as e:
        raise FileNotFoundError(
            f"Template '{access_template_name}' not found in '{resources_dir}'"
        ) from e

    access_policy_document = access_template.render()

    try:
        # Create or update the policy
        policy_name = f"{role_name}-policy"
        try:
            policy = iam.get_policy(
                PolicyArn=f'arn:aws:iam::{session.client("sts").get_caller_identity()["Account"]}:policy/{policy_name}'
            )
            policy_arn = policy["Policy"]["Arn"]
            print(f"Policy '{policy_name}' already exists. Updating policy.")
            iam.create_policy_version(
                PolicyArn=policy_arn,
                PolicyDocument=access_policy_document,
                SetAsDefault=True,
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                policy = iam.create_policy(
                    PolicyName=policy_name,
                    PolicyDocument=access_policy_document,
                    Description=f"Policy for full access to CloudFormation, Route53, S3, SecretsManager, and KMS for role {role_name}",
                )
                policy_arn = policy["Policy"]["Arn"]
                print(f"Policy '{policy_name}' created.")
            else:
                raise OSError(
                    f"An AWS error occurred: {e.response['Error']['Message']}"
                ) from e

        # Check if the policy is already attached to the role
        attached_policies = iam.list_attached_role_policies(RoleName=role_name)[
            "AttachedPolicies"
        ]
        if any(p["PolicyArn"] == policy_arn for p in attached_policies):
            print(f"Policy '{policy_name}' is already attached to role '{role_name}'.")
        else:
            # Attach the policy to the role
            iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
            print(
                f"Policy '{policy_name}' attached to role '{role_name}' successfully."
            )

    except ClientError as e1:
        raise OSError(
            f"An AWS error occurred while attaching the policy to the role: {e1.response['Error']['Message']}"
        ) from e


def create_roles(**kwargs):
    """execute the role tasks"""
    profile_name = kwargs.get("aws_profile")
    role_name = kwargs.get("automation_role")

    if not profile_name or not role_name:
        raise ValueError(
            "Both 'profile_name' and 'role_name' must be provided.  Did you run 'core configure' first?"
        )

    print(
        f"Checking core-autmation roles for profile '{profile_name}' and role '{role_name}'"
    )

    try:
        # Create a boto3 session using the specified profile
        session = boto3.Session(profile_name=profile_name)

        # Initialize IAM client using the session
        iam = session.client("iam")

        # Set the path to the templates
        resources_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "resources", "roles", role_name
        )

        # Check if the resources directory exists
        if not os.path.exists(resources_dir):
            raise ValueError("Role policy has not been defined")

        create_trust_policy(iam, role_name, resources_dir)

        create_access_policy(iam, session, role_name, resources_dir)

    except ClientError as e:
        raise OSError(f"An AWS error occurred: {e.response['Error']['Message']}") from e
    except FileNotFoundError as e:
        raise ValueError(f"File error: {str(e)}") from e
    except NoCredentialsError as e:
        raise ValueError(
            "No AWS credentials found. Please make sure you have logged in using AWS SSO or have credentials configured."
        ) from e
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {str(e)}") from e  # noqa: E722


def detach_policy(iam, role_name):
    """detatch all policies from the role so they can be deleted"""
    # Detach all policies attached to the role
    attached_policies = iam.list_attached_role_policies(RoleName=role_name)[
        "AttachedPolicies"
    ]
    for policy in attached_policies:
        iam.detach_role_policy(RoleName=role_name, PolicyArn=policy["PolicyArn"])
        print(f"Detached policy '{policy['PolicyArn']}' from role '{role_name}'.")


def delete_policy(iam, session, role_name):
    """delete all policy associated with the role based on the policy name prefix"""
    # Delete the policy
    policy_name = f"{role_name}-policy"
    account_id = session.client("sts").get_caller_identity()["Account"]
    policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"

    try:
        policy_versions = iam.list_policy_versions(PolicyArn=policy_arn)["Versions"]
        for version in policy_versions:
            if not version["IsDefaultVersion"]:
                iam.delete_policy_version(
                    PolicyArn=policy_arn, VersionId=version["VersionId"]
                )
        iam.delete_policy(PolicyArn=policy_arn)
        print(f"Deleted policy '{policy_arn}'.")
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchEntity":
            raise OSError(
                f"An AWS error occurred while deleting the policy: {e.response['Error']['Message']}"
            ) from e


def delete_roles(**kwargs):
    """Delete core-automatoin roles"""
    profile_name = kwargs.get("aws_profile")
    role_name = kwargs.get("automation_role")

    if not profile_name or not role_name:
        raise ValueError("Both 'profile_name' and 'role_name' must be provided.")

    try:
        # Create a boto3 session using the specified profile
        session = boto3.Session(profile_name=profile_name)

        # Initialize IAM client using the session
        iam = session.client("iam")

        # Check if the role exists
        try:
            iam.get_role(RoleName=role_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                print(f"Role '{role_name}' does not exist.")
                return
            else:
                raise OSError(
                    f"An AWS error occurred: {e.response['Error']['Message']}"
                ) from e

        detach_policy(iam, role_name)

        delete_policy(iam, session, role_name)

        # Delete the role
        iam.delete_role(RoleName=role_name)
        print(f"Deleted role '{role_name}' successfully.")

    except ClientError as e:
        raise OSError(f"An AWS error occurred: {e.response['Error']['Message']}") from e
    except NoCredentialsError as e:
        raise ValueError(
            "No AWS credentials found. Please make sure you have logged in using AWS SSO or have credentials configured."
        ) from e
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {str(e)}") from e


def unit_roles(**kwargs):
    """add or delete core automation roles"""
    print(json.dumps(dict(kwargs), indent=4))
    delete = kwargs.get("delete", False)
    if delete:
        delete_roles(**kwargs)
    else:
        create_roles(**kwargs)


def unit_all(**kwargs):
    """execute all the tasks"""
    print("All")


def unit_resources(**kwargs):
    """execute the resource tasks"""
    print("Resources")


CHOICES = {
    "all": (
        "Initilize the Core platform and deploy things such as the custom resource",
        unit_all,
    ),
    "resources": ("Deploys common CloudFormation Resources", unit_resources),
    "roles": ("Initialize the roles for the Core platform", unit_roles),
}


def add_init_parser(subparsers):
    """add the clean parser"""

    description = "Initialize the Core platform and deploy things such as the custom resource handler"

    subparser = subparsers.add_parser(
        "init",
        choices=CHOICES,
        usage="core engine init [<unit>] [<options>]",
        description=description,
        help=description,
    )
    subparser.set_group_title(0, "Init units")
    subparser.set_group_title(1, "Available options")

    subparser.add_argument("unit", choices=CHOICES.keys())

    subparser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Delete the roles, resources, or all",
    )

    return {"init": (description, execute_init)}


def execute_init(**kwargs):
    """execute the command"""
    task = kwargs.get("unit", None)
    if task:
        CHOICES[task][1](**kwargs)
    else:
        print("No task specified")
