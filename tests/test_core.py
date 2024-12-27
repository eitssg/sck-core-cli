import os
import pytest
from core_automation import register_module, parse_args, __version__


def test_core_info():

    registration_data = {
        "name": "core",
        "description": "Core Automation Module",
        "version": __version__,
    }

    name, description, version = register_module(**registration_data)

    assert registration_data["name"] == name
    assert registration_data["description"] == description
    assert registration_data["version"] == version

    os.environ["CLIENT"] = "test_client"
    os.environ["AWS_PROFILE"] = "test_profile"

    args = ["info"]

    pargs = parse_args(args)

    data = vars(pargs)

    assert "info" == data.get("command")
    assert "test_client" == data.get("client")
    assert "test_profile" == data.get("aws_profile")
    assert "test_client" == os.getenv("CLIENT")
    assert "test_profile" == os.getenv("AWS_PROFILE")


def test_core_info_no_client():

    registration_data = {
        "name": "core",
        "description": "This is the core module for the SCK.",
        "version": __version__,
    }

    name, description, version = register_module(**registration_data)

    assert registration_data["name"] == name
    assert registration_data["description"] == description
    assert registration_data["version"] == version

    if "CLIENT" in os.environ:
        del os.environ["CLIENT"]
    if "AWS_PROFILE" in os.environ:
        del os.environ["AWS_PROFILE"]

    args = ["--client", "test_client", "info"]

    pargs = parse_args(args)

    data = vars(pargs)
    print(data)
    print(dict(os.environ))

    assert "info" == data.get("command")
    assert "test_client" == data.get("client")
    assert "test_profile" == data.get("aws_profile")
    assert "test_client" == os.getenv("CLIENT")
    assert "test_profile" == os.getenv("AWS_PROFILE")


def test_core_info_no_profile():

    registration_data = {
        "name": "core",
        "description": "This is the core module for the SCK.",
    }

    name, description = register_module(**registration_data)

    assert registration_data["name"] == name
    assert registration_data["description"] == description

    if "CLIENT" in os.environ:
        del os.environ["CLIENT"]
    if "AWS_PROFILE" in os.environ:
        del os.environ["AWS_PROFILE"]

    args = ["--client", "test_client", "--aws-profile", "test_profile", "info"]

    pargs = parse_args(args)

    data = vars(pargs)
    print(data)
    print(dict(os.environ))

    assert "info" == data.get("command")
    assert "test_client" == data.get("client")
    assert "test_profile" == data.get("aws_profile")
    assert "test_client" == os.getenv("CLIENT")
    assert "test_profile" == os.getenv("AWS_PROFILE")
