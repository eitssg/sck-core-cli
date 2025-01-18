import os
from rich.table import Table
from rich import box

import core_helper.aws as aws
import core_framework as util
from core_framework.models import ActionDefinition
from core_framework.constants import (
    P_REGION,
    P_TEMPLATE,
    P_STACK_NAME,
    P_STACK_PARAMETERS,
    P_TAGS,
)

import core_logging as log

from ..common import cprint, get_input


def generate_parameters(data: dict):
    """
    Generate the parameters for the stack
    """
    stack_parameters = data.get("stack_parameters", None)

    if stack_parameters is None:
        raise Exception("Template Paramters must be specified")

    if not isinstance(data, dict):
        raise ValueError("Stack Paraeters must be a dictionary")

    return aws.transform_stack_parameter_hash(stack_parameters)


# function will delete the changeset if it exists
def delete_change_set_if_exists(stack_name, region):

    cprint(f"Checking if change set {stack_name}-change-set exists...")

    cloudformation = aws.cfn_client(region=region)

    # Check if the change set exists
    try:
        response = cloudformation.describe_change_set(
            ChangeSetName=f"{stack_name}-change-set", StackName=stack_name
        )
        if response["Status"] == "CREATE_COMPLETE":
            cprint("Change set exists and is complete.")
        elif response["Status"] == "FAILED":
            cprint("Change set exists and has failed.")
    except cloudformation.exceptions.ChangeSetNotFoundException:
        cprint("Change set does not exist.  Continuing...")
        return

    # If the change set exists, delete it
    cprint(f"Deleting change set {stack_name}-change-set...")
    cloudformation.delete_change_set(
        ChangeSetName=f"{stack_name}-change-set", StackName=stack_name
    )

    try:
        # Wait for the change set to be deleted
        waiter = cloudformation.get_waiter("change_set_delete_complete")
        waiter.wait(StackName=stack_name, ChangeSetName=f"{stack_name}-change-set")
    except ValueError as e:
        cprint(e)

    cprint("Change set deleted successfully.")


# Create a change set for the stack
def create_stack_change_set(data: dict, region: str):

    stack_name = data[P_STACK_NAME]
    template = data[P_TEMPLATE]

    tags = data.get(P_TAGS, {})

    # delete the change set if it exists
    delete_change_set_if_exists(stack_name, region)

    cprint(f"Creating change set for stack {stack_name}...")
    cprint("This may take a while...")

    cloudformation = aws.cfn_client(region=region)

    # Create a change set for the stack
    response = cloudformation.create_change_set(
        StackName=stack_name,
        TemplateBody=open(template).read(),
        Parameters=generate_parameters(data),
        Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
        ChangeSetName=f"{stack_name}-change-set",
        ChangeSetType="UPDATE",
        Tags=aws.transform_tag_hash(tags),
    )

    # if the response error is FAILED then query the reason and print on the console
    if (
        "ResponseMetadata" in response
        and response["ResponseMetadata"]["HTTPStatusCode"] != 200
    ):
        if response["ResponseMetadata"]["HTTPStatusCode"] == 400:
            reason = response["ResponseMetadata"]["HTTPHeaders"]["x-amzn-errortype"]
            cprint(f"Error creating change set: {reason}")
        else:
            raise Exception(f"Error creating change set: {response}")

    try:
        # wait for the change set to be created
        waiter = cloudformation.get_waiter("change_set_create_complete")
        waiter.wait(StackName=stack_name, ChangeSetName=f"{stack_name}-change-set")
    except Exception:
        pass

    # query the change set and get its status.  If failed, print the failure reason
    response = cloudformation.describe_change_set(
        ChangeSetName=f"{stack_name}-change-set", StackName=stack_name
    )
    if response["Status"] == "FAILED":
        reason = response["StatusReason"]
        cprint(f"Cannot create change set: {reason}")
        cprint("Since there is no change set, we will stop this deployment.")
        return {"Status": "ABORT"}

    cprint("Change set created successfully.")

    return response


# fucntion will read all the values that will be changes from the changeset and siplay the changes in a table
def display_stack_change_set(stack_name: str, region: str):

    cloudformation = aws.cfn_client(region=region)

    # Get the change set
    response = cloudformation.describe_change_set(
        ChangeSetName=f"{stack_name}-change-set", StackName=stack_name
    )
    changes = response["Changes"]

    cprint("The following changes will be made:")

    # Create a table to display the changes
    table = Table(box=box.SIMPLE)
    table.add_column("Action", style="cyan", no_wrap=True)
    table.add_column("Logical ID", style="cyan", no_wrap=True)
    table.add_column("Resource Type", style="cyan", no_wrap=True)
    table.add_column("Replacement", style="cyan", no_wrap=True)
    table.add_column("Physical ID", style="cyan", no_wrap=True)
    table.add_column("Target", style="cyan", no_wrap=True)

    # Display the changes
    for change in changes:

        resource_change = change.get("ResourceChange")

        if resource_change:

            action = resource_change.get("Action", "")
            logical_id = resource_change.get("LogicalResourceId", "")
            physical_id = resource_change.get("PhysicalResourceId", "")
            replacement = resource_change.get("Replacement", "")
            change_type = resource_change.get("ResourceType")

            details = resource_change.get("Details")
            if details:
                for resource in details:
                    change_source = resource.get("ChangeSource", "")
                    target = resource.get("Target", "")
                    target_name = ""

                    if change_source == "DirectModification":
                        if "Name" in target:
                            target_name = resource["Target"]["Name"]
                        elif "Attribute" in target:
                            target_name = resource["Target"]["Attribute"]

                    elif change_source == "ResourceReference":
                        if "Name" in target:
                            target_name = resource["Target"]["Name"]

                    table.add_row(action, logical_id, change_type, replacement, physical_id, target_name)
            else:
                table.add_row(action, logical_id, change_type, replacement, physical_id, target_name)

    cprint(table)


def deploy_stack_change(stack_name: str, region: str):

    cprint(f"Deploying change set for stack {stack_name}...")
    cprint("This may take a while...")

    cloudformation = aws.cfn_client(region=region)

    # Execute the change set.  Ensure capabilities are et to allow IAM changes
    response = cloudformation.execute_change_set(
        ChangeSetName=f"{stack_name}-change-set", StackName=stack_name
    )
    # if the response has an error, rais an exception
    if (
        "ResponseMetadata" in response
        and response["ResponseMetadata"]["HTTPStatusCode"] != 200
    ):
        raise Exception(f"Error executing change set: {response}")

    try:
        # wait for the change set to be
        waiter = cloudformation.get_waiter("stack_update_complete")
        waiter.wait(StackName=stack_name)
    except ValueError as e:
        cprint(e)


def check_stack_exists(stack_name: str, region: str):

    cloudformation = aws.cfn_client(region=region)
    stack_exists = False
    try:
        stacks = cloudformation.describe_stacks()
        for stack in stacks["Stacks"]:
            if stack["StackName"] == stack_name:
                stack_exists = True
                break
    except Exception as e:
        cprint(e)
        stack_exists = False

    return stack_exists


def delete_stack_if_in_bad_status(stack_name: str, region: str):

    if not check_stack_exists(stack_name, region):
        return True

    # if the current stack status is ROLLBACK_COMPLETE, DELETE it
    cloudformation = aws.cfn_client(region=region)
    stack = cloudformation.describe_stacks(StackName=stack_name)
    stack_status = stack["Stacks"][0]["StackStatus"]

    # If a Rollback is complete, then delete the stack
    if stack_status == "ROLLBACK_COMPLETE":
        cprint(f"Stack {stack_name} is in status {stack_status}.  Deleting stack...")
        delete_stack(stack_name, region)
        return True

    # if the current stack is in progress, then raise an exception
    if stack_status in [
        "CREATE_IN_PROGRESS",
        "UPDATE_IN_PROGRESS",
        "DELETE_IN_PROGRESS",
    ]:
        raise Exception(
            f"Stack {stack_name} is in status {stack_status}.  Cannot deploy stack while in progress."
        )


# function will deploy the cloudformation stack using the yaml template 'cfn-core-api-app.yaml'
def deploy_stack(data: dict, region: str):

    stack_name = data[P_STACK_NAME]
    template = data[P_TEMPLATE]
    tags = data.get(P_TAGS, {})

    cprint(f"Deploying stack {stack_name}...")
    cprint("This may take a while...")

    cloudformation = aws.cfn_client(region=region)

    # Deploy the CloudFormation stack.  Make sure the stack appears on the AWS "Appications" console page.
    response = cloudformation.create_stack(
        StackName=stack_name,
        Parameters=generate_parameters(data),
        TemplateBody=open(template).read(),
        Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
        Tags=aws.transform_tag_hash(tags),
    )

    # wait for the stack creation to complete
    waiter = cloudformation.get_waiter("stack_create_complete")
    waiter.wait(StackName=stack_name)

    return response


# Delete the stack and wait for it to be completed
def delete_stack(stack_name: str, region: str):

    cprint(f"Deleting stack {stack_name}...")
    cprint("This may take a while...")

    cloudformation = aws.cfn_client(region=region)

    response = cloudformation.delete_stack(StackName=stack_name)

    # wait for the stack deletion to complete
    waiter = cloudformation.get_waiter("stack_delete_complete")
    waiter.wait(StackName=stack_name)

    return response


# Use aws boto3 to verify the stack yaml file is correct and can be deployed
def verify_stack_template(stack_name: str, template: str, region: str):

    cprint(f"Validating stack {stack_name}...")
    cprint("This may take a while...")

    cloudformation = aws.cfn_client(region=region)

    response = cloudformation.validate_template(TemplateBody=open(template).read())
    # if the response has an error, rais an exception
    if (
        "ResponseMetadata" in response
        and response["ResponseMetadata"]["HTTPStatusCode"] != 200
    ):
        raise Exception(f"Error validating template: {response}")

    cprint("The stack is good to go!")

    return True


def start_deploy_stack(**kwargs):

    # Configure logging
    log.getLogger("boto3").setLevel(log.WARNING)
    log.getLogger("botocore").setLevel(log.WARNING)
    log.getLogger("nose").setLevel(log.WARNING)
    log.getLogger("urllib3").setLevel(log.WARNING)

    stack_name = kwargs.get(P_STACK_NAME)
    template = kwargs.get(P_TEMPLATE)
    region = kwargs.get("region", util.get_region())

    if not stack_name:
        raise Exception("Please provide the stack name as an argument.")

    if not template:
        raise Exception("Please provide the template file as an argument.")

    cprint(f"Deploying CloudFromation Stack: [orange]{stack_name}[/orange]")

    # raise an exception if the yaml file doesn't exist
    if not os.path.exists(template):
        raise Exception(f"{template} does not exist")

    # verify the stack
    verify_stack_template(stack_name, template, region)

    delete_stack_if_in_bad_status(stack_name, region)

    cprint(f"Checking if stack {stack_name} exists...")
    stack_exists = check_stack_exists(stack_name, region)
    if stack_exists:
        result = create_stack_change_set(kwargs, region)
        if result["Status"] == "ABORT":
            cprint("No changes.")
            return
        display_stack_change_set(stack_name, region)
        result = get_input("Do you want to deploy the change set?", ["Y", "n"], "y")
        if result.lower() == "y":
            deploy_stack_change(stack_name, region)
        else:
            cprint("Change set deployment aborted.")
    else:
        cprint("Stack does not exist.  Deploying new stack...")
        deploy_stack(kwargs, region)

    cprint("Process complete.")


def start_action(action_definition: ActionDefinition):
    parms = action_definition.Params
    data = {
        P_REGION: parms.Region,
        P_TEMPLATE: parms.TemplateUrl,
        P_STACK_NAME: parms.StackName,
        P_STACK_PARAMETERS: parms.StackParameters,
        P_TAGS: parms.Tags,
    }
    start_deploy_stack(**data)
