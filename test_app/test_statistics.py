import json


def test_statistics_request(simulator_configuration, record_file_name, client):
    response = client.post(
        "/workspaces/",
        json=simulator_configuration,
    )
    assert response.status_code == 200
    simulator_id = response.json()["id"]

    resp = client.get(
        f"/statistics/graph/{simulator_id}",
    )

    requests = 0
    with open(record_file_name, encoding="utf-8") as f:
        for line in f:
            timing, operation = line.strip().split("\t")
            resp = client.post(
                f"/workspaces/play/{simulator_id}",
                json={"operation": operation},
            )
            requests += 1
            if requests > 50:
                break

    resp = client.get(
        f"/statistics/graph/{simulator_id}",
    )
