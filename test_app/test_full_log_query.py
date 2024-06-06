import json


def test_full_log(simulator_configuration, record_file_name, client):
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

            given_delay = resp.json()["logs"][-1]["delay"]

            requests += 1

    resp = client.get(
        f"/workspaces/logs/{simulator_id}",
    )

    assert len(resp.json()) == requests + 1
