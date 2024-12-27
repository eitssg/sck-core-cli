"""
Send the event to the lambda handler either in AWS or in local mode.
"""

from core_framework import is_local_mode

import core_helper.aws as aws

from core_execute.handler import handler as lambda_handler


def execute_event(event: dict) -> dict:
    """
    Execute the event in either local mode or in AWS lambda mode.
    """
    if is_local_mode():

        result = lambda_handler(event)

    else:

        arn = "arn:aws:lambda:us-east-1:123456789012:function:core-execute"
        role = "CoreAutomationExecuteRole"

        result = aws.invoke_lambda(arn, event, role)

    return result if result is not None else {}
