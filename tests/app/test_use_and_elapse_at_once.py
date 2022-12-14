import json

from fastapi.testclient import TestClient

from simaple.app.interface.web import app

client = TestClient(app)


def test_read_main(workspace_configuration, record_file_name):
    response = client.post(
        "/workspaces/",
        json=workspace_configuration,
    )
    assert response.status_code == 200
    workspace_id = response.json()["id"]

    requests = 0
    previous_delay = 0

    with open(record_file_name, encoding="utf-8") as f:
        for line in f:
            timing, action = line.split("\t")
            action = json.loads(action)

            if action["method"] == "use":
                resp = client.post(
                    f"/workspaces/use_and_elapse/{workspace_id}",
                    json={"name": action["name"]},
                )

            given_delay = resp.json()["delay"]
            assert given_delay == 0
