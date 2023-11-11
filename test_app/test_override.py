import json
import os
from pathlib import Path

import pytest


@pytest.fixture(name="sample_ckpt")
def fixture_sample_ckpt():
    with open(
        Path(os.path.dirname(__file__)) / "application" / "checkpoint.json",
        encoding="utf-8",
    ) as f:
        ckpt = json.load(f)

    return ckpt


def test_override(simulator_configuration, record_file_name, client, sample_ckpt):
    response = client.post(
        "/workspaces/",
        json=simulator_configuration,
    )
    assert response.status_code == 200
    simulator_id = response.json()["id"]

    response = client.post(
        f"/workspaces/override/{simulator_id}",
        json={"store_ckpt": sample_ckpt, "callbacks": []},
    )
    assert response.status_code == 200

    with open(record_file_name, encoding="utf-8") as f:
        actions = [line.split("\t")[1] for line in f]

    for idx in range(25):
        client.post(
            f"/workspaces/play/{simulator_id}",
            json=json.loads(actions[idx]),
        )

    response = client.post(
        f"/workspaces/override/{simulator_id}",
        json=sample_ckpt,
    )
    assert response.status_code == 409
