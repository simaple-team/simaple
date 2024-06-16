def test_full_log(simulator_configuration, client):
    response = client.post(
        "/workspaces/",
        json=simulator_configuration,
    )
    assert response.status_code == 200
    simulator_id = response.json()["id"]

    resp = client.post(
        f"/workspaces/run/{simulator_id}",
        json={"plan": """
CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"

CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"
"""},
    )
    assert len(resp.json()) == 13

    resp = client.post(
        f"/workspaces/run/{simulator_id}",
        json={"plan": """
CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"

CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"
x4 CAST "플레임 스윕 VI"
"""},
    )
    assert len(resp.json()) == 13 + 4


def test_create_from_simulator(client):
    response = client.post(
        "/workspaces/plan",
        json={
            "plan": """
/*
configuration_name: "baseline_configuration"
author: "Alice"
data:
    simulation_setting:
        tier: Legendary
        jobtype: archmagetc
        job_category: 1 # mage
        level: 270
        passive_skill_level: 0
        combat_orders_level: 1
        artifact_level: 40
*/
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0  

"""
        },
    )
    assert response.status_code == 200
