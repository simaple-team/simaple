import json


def test_latest_log_query(simulator_configuration, record_file_name, client):
    response = client.post(
        "/workspaces/",
        json=simulator_configuration,
    )
    assert response.status_code == 200
    simulator_id = response.json()["id"]

    requests = 0

    with open(record_file_name, encoding="utf-8") as f:
        for line in f:
            timing, operation = line.strip().split("\t")
            resp = client.post(
                f"/workspaces/play/{simulator_id}",
                json={"operation": operation},
            )

            requests += 1

    resp_latest = client.get(
        f"/workspaces/logs/{simulator_id}/latest",
    )

    resp_end = client.get(
        f"/workspaces/logs/{simulator_id}/{requests}",
    )

    assert resp_end.json() == resp_latest.json()
