from core_automation.execute.simulate import ActionEvent


def test_action_event():

    deployment_detais = {
        "portfolio": "operations-kit",
        "app": "bigapp",
        "branch": "branch/23/jdb/pdx-23",
        "build": "build-1",
    }

    data = {
        "action": "test",
        "deployment_details": deployment_detais,
    }

    try:
        action_event = ActionEvent(**data)

        assert action_event is not None

    except Exception as e:
        assert False, f"Error: {e}"

    assert True
