from typing import Self

import argparse
import time
import json
import os
import yaml

from pydantic import BaseModel, Field, model_validator

import core_framework as util

from core_framework.constants import (
    TP_DEPLOYMENT_DETAILS,
    TP_TASK,
    TP_IDENTITY,
    TP_ACTIONS,
    TP_STATE,
    DD_SCOPE,
    DD_APP,
    DD_BRANCH,
    DD_CLIENT,
    DD_BUILD,
    DD_PORTFOLIO,
    DD_COMPONENT,
    DD_BRANCH_SHORT_NAME,
)

from .invoke import execute_event


def deploy(**kwargs):
    print("Deploying")


def release(**kwargs):
    print("Releasing")


def teardown(**kwargs):
    print("Tearing down")


def unknown(**kwargs):
    print("Unknown action")


ACTIONS = {"deploy": deploy, "release": release, "teardown": teardown}


def _get_args():
    parser = argparse.ArgumentParser(
        description="Component Compiler for the Action Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "action", choices=["deploy", "release", "teardown"], help="Action to perform"
    )
    parser.add_argument(
        "-c", "--client", help="Client name for selecting config", required=True
    )
    parser.add_argument("-p", "--portfolio", help="Portfolio name", required=True)
    parser.add_argument("-a", "--app", help="Application name", required=True)
    parser.add_argument("-b", "--branch", help="Branch name", required=True)
    parser.add_argument("-n", "--build", help="Build number", required=True)
    parser.add_argument("--client-vars", help="Client vars")
    parser.add_argument(
        "--aws-profile",
        default=None,
        help="Select which profile to use from your ~/.aws/credentials file.",
    )
    args = parser.parse_args()

    if args.action is None:
        raise ValueError("action is required to simulate.")

    return args


def run(**kwargs):

    action = kwargs.get("action", None)

    # Run the action
    ACTIONS.get(action, unknown)(**kwargs)

    event = __generate_event()
    # exit('event={}'.format(json.dumps(event, indent=2)))

    while True:
        event = execute_event(event)

        # print("StepFunction: Transitioning to state '{}'".format(event["FlowControl"]))

        # print("FlowControl: {}".format(event["FlowControl"]))
        if event["FlowControl"] == "wait":
            time.sleep(15)
        elif event["FlowControl"] == "success":
            print("====== SUCCESS! ======")
            print(json.dumps(event, indent=2))
            f = open("simulate-response.txt", "w")
            f.write(json.dumps(event, indent=2))
            f.close()
            break
        elif event["FlowControl"] == "failure":
            print("====== FAILURE! ======")
            print(json.dumps(event, indent=2))
            f = open("simulate-response.txt", "w")
            f.write(json.dumps(event, indent=2))
            f.close()
            break
        elif event["FlowControl"] == "execute":
            pass
        else:
            print(
                "====== ERROR: Unknown flow control '{}' ======".format(
                    event["FlowControl"]
                )
            )
            break


def __get_client_vars(client: str) -> dict:
    client_vars = f"../../../{client}-config/client-vars.yaml"
    with open(client_vars) as f:
        return yaml.safe_load(f.read())
    for key in client_vars:
        os.environ[key] = "{}".format(client_vars[key])
    return client_vars


def __generate_event(**kwargs):

    action = kwargs.get("action", None)
    client = kwargs.get("client, None")
    portfolio = kwargs.get("portfolio", None)
    app = kwargs.get("app", None)
    branch = kwargs.get("branch", None)
    build = kwargs.get("build", None)

    aws_profile = kwargs.get("aws_profile", "default")

    client_vars = __get_client_vars(client)

    print("client_vars={}".format(json.dumps(client_vars, indent=2)))

    os.environ["AWS_PROFILE"] = aws_profile

    branch_short_name = util.branch_short_name(branch)

    bucket_region = client_vars["CLIENT_REGION"]

    bucket_name = "{}{}-core-automation-{}".format(
        client_vars.get("SCOPE_PREFIX", ""),
        client_vars["CLIENT_NAME"],
        client_vars["CLIENT_REGION"],
    )

    delivered_by = (
        os.environ["DELIVERED_BY"] if "DELIVERED_BY" in os.environ else "automation"
    )

    event = {
        "Actions": {
            "Key": "artefacts/{}/{}/{}/{}/{}.actions".format(
                portfolio, app, branch_short_name, build, action
            ),
            "BucketRegion": bucket_region,
            "BucketName": bucket_name,
        },
        "DeploymentDetails": {
            "DeliveredBy": delivered_by,
            "Portfolio": portfolio,
            "App": app,
            "Branch": branch,
            "Build": build,
            "BranchShortName": branch_short_name,
        },
        "Identity": "prn:{}:{}:{}:{}".format(portfolio, app, branch_short_name, build),
        "Task": action,
        "State": {
            "Key": "artefacts/{}/{}/{}/{}/{}.state".format(
                portfolio, app, branch_short_name, build, action
            ),
            "VersionId": "new",
            "BucketRegion": bucket_region,
            "BucketName": bucket_name,
        },
    }

    return event


class ClientDetails(BaseModel):

    Name: str | None = Field(default=None, alias="name")
    Region: str = Field(default="ap-southeast-1", alias="region")
    ScopePrefix: str = Field(default="", alias="scope_prefix")


class DeploymenDetails(BaseModel):

    Scope: str | None = Field(default=None, alias="scope")

    Client: str | None = Field(default=None, alias="client")

    Portfolio: str | None = Field(default=None, alias="portfolio")
    App: str | None = Field(default=None, alias="app")
    Branch: str | None = Field(default=None, alias="branch")
    BranchShortName: str | None = Field(default=None, alias="branch_short_name")
    Build: str | None = Field(default=None, alias="build")
    Component: str | None = Field(default=None, alias="component")

    Environment: str | None = Field(default=None, alias="environment")
    DataCenter: str | None = Field(default=None, alias="data_center")
    Ecr: str | None = Field(default=None, alias="ecr")
    Tags: dict | None = Field(default=None, alias="tags")
    DeliveredBy: str = Field(default="automation", alias="delivered_by")

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if not self.Client:
            self.Client = util.get_client()
        if not self.Scope:
            self.Scope = self.generate_scope()
        if not self.BranchShortName:
            self.BranchShortName = util.branch_short_name(self.Branch or "")
        return self

    def generate_scope(self) -> str | None:

        if not self.Portfolio:
            return util.constants.SCOPE_CLIENT if self.Client else None

        if not self.App:
            return util.constants.SCOPE_PORTFOLIO

        if not self.Branch:
            return util.constants.SCOPE_APP

        if not self.Build:
            return util.constants.SCOPE_BRANCH

        return (
            util.constants.SCOPE_COMPONENT
            if self.Component
            else util.constants.SCOPE_BUILD
        )

    def get_artefact_prefix(self):
        """
        Returns the artefact prefix based on the scope of the deployment details

        The bucket name, FYI, is unique to the client.

        Returns:
            _type_: _description_
        """
        prefix = "artefacts"
        if self.Scope == util.constants.SCOPE_CLIENT:
            return f"{prefix}/{self.Client}"
        if self.Scope == util.constants.SCOPE_PORTFOLIO:
            return f"{prefix}/{self.Portfolio}"
        if self.Scope == util.constants.SCOPE_APP:
            return f"{prefix}/{self.Portfolio}/{self.App}"
        if self.Scope == util.constants.SCOPE_BRANCH:
            return f"{prefix}/{self.Portfolio}/{self.App}/{self.BranchShortName}"
        if self.Scope == util.constants.SCOPE_BUILD:
            return f"{prefix}/{self.Portfolio}/{self.App}/{self.BranchShortName}/{self.Build}"
        if self.Scope == util.constants.SCOPE_COMPONENT:
            return f"{prefix}/{self.Portfolio}/{self.App}/{self.BranchShortName}/{self.Build}/{self.Component}"
        return prefix


class BucketInfo(BaseModel):

    Key: str | None = Field(default=None, alias="key")
    VersionId: str = Field(default="new", alias="version_id")
    BucketRegion: str = Field(
        alias="bucket_region", default_factory=util.get_bucket_region
    )
    BucketName: str = Field(alias="bucket_name", default_factory=util.get_bucket_name)


class ActionEvent(BaseModel):

    Task: str = Field(alias="action")
    Identity: str | None = Field(default=None, alias="identity")
    DeploymentDetails: DeploymenDetails = Field(
        alias="deployment_details", default_factory=lambda: DeploymenDetails()
    )
    Actions: BucketInfo = Field(alias="actions", default_factory=lambda: BucketInfo())
    State: BucketInfo = Field(alias="state", default_factory=lambda: BucketInfo())

    @model_validator(mode="after")
    def validate_model_after(self) -> Self:

        dd = self.DeploymentDetails
        if dd:

            self.Identity = util.get_identity(dd.model_dump())

            artefact_prefix = dd.get_artefact_prefix()

            # Generate Actions.Key
            self.Actions.Key = f"{artefact_prefix}/{self.Task}.actions"

            # Generate State.Key
            self.State.Key = f"{artefact_prefix}/{self.Task}.state"

        return self
