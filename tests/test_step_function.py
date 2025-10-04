import pytest
import json

from core_framework.models import (
    TaskPayload,
    DeploymentDetails as DeploymentDetailsClass,
)


from core_runner.handler import handler


@pytest.fixture
def task_payload():

    task_payload = TaskPayload(
        Task="deploy",
        DeploymentDetails=DeploymentDetailsClass(
            Client="Client",
            Portfolio="Portfolio",
            Environment="Environment",
            Scope="portfolio",
            DataCenter="DataCenter",
        ),
    )

    return task_payload


def test_step_function_client(task_payload: TaskPayload):

    region = "us-east-1"

    dd = task_payload.deployment_details

    event = task_payload.model_dump()

    result = handler(event, None)

    assert result is not None

    print("Unit Test Execution Results:")
    print(json.dumps(result, indent=2))

    execution_arn = f"arn:aws:states:{region}:123456789012:execution:sck-core-step-function-state-machine:exec-{dd.client}-{dd.portfolio}-{dd.environment}-1234"

    assert result["executionArn"] == execution_arn
