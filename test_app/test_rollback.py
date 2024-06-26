import json


def test_rollback(simulator_configuration, record_file_name, client):
    response = client.post(
        "/workspaces/",
        json=simulator_configuration,
    )
    assert response.status_code == 200
    simulator_id = response.json()["id"]

    with open(record_file_name, encoding="utf-8") as f:
        operations = [line.strip().split("\t")[1] for line in f]

    for idx in range(25):
        resp = client.post(
            f"/workspaces/play/{simulator_id}",
            json={"operation": operations[idx]},
        )

    saved_resp = resp

    for idx in range(25, 50):
        resp = client.post(
            f"/workspaces/play/{simulator_id}",
            json={"operation": operations[idx]},
        )

    rollback_resp = client.post(
        f"/workspaces/rollback/{simulator_id}/24",
    )

    assert rollback_resp.status_code == 200

    new_resp = client.post(
        f"/workspaces/play/{simulator_id}",
            json={"operation": operations[24]},
    )

    assert saved_resp.json() == new_resp.json()
