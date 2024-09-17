from simaple.wasm.workspace import runSimulatorWithPlanConfig


def test_create_simulator_from_plan():
    simulation_response = runSimulatorWithPlanConfig(
        """
/*
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
*/
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0  
"""
    )
    assert isinstance(simulation_response, list)
