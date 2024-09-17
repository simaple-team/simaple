from simaple.wasm.workspace import (
    runSimulatorWithPlanConfig,
    runSimulatorWithPlanConfigUsingCache,
)


def test_create_simulator_from_plan():
    simulation_response = runSimulatorWithPlanConfig(
        """
configuration_name: "BaselineCharacterProvider"
author: "Alice"
data:
    tier: Legendary
    jobtype: archmagetc
    job_category: 1 # mage
    level: 270
    artifact_level: 40
    passive_skill_level: 0
    combat_orders_level: 1
simulation_setting: {}
---
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0  
"""
    )
    assert isinstance(simulation_response, list)


def test_create_simulator_from_plan_using_cache():
    plan = """
configuration_name: "BaselineCharacterProvider"
author: "Alice"
data:
    tier: Legendary
    jobtype: archmagetc
    job_category: 1 # mage
    level: 270
    artifact_level: 40
    passive_skill_level: 0
    combat_orders_level: 1
simulation_setting: {}
---
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0  
"""
    simulation_response = runSimulatorWithPlanConfigUsingCache(plan, {})
    first_logs = simulation_response.logs
    assert len(simulation_response.cache) == 1

    simulation_response = runSimulatorWithPlanConfigUsingCache(
        plan, simulation_response.cache
    )
    assert len(simulation_response.cache) == 1
    assert first_logs == simulation_response.logs
