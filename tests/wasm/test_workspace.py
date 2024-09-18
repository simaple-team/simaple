from simaple.container.simulation import SimulationEnvironment
from simaple.wasm.workspace import computeSimulationEnvironmentFromProvider, runWithGivenEnvironment


def test_get_serialized_character_provider_then_run():
    plan = """
author: "Alice"
provider:
    name: "BaselineCharacterProvider"
    data:
        tier: Legendary
        jobtype: archmagetc
        job_category: 1 # mage
        level: 270
        artifact_level: 40
        passive_skill_level: 0
        combat_orders_level: 1
    environment: {}
---
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0  
"""
    serialized_character_provider = computeSimulationEnvironmentFromProvider(plan)
    assert isinstance(serialized_character_provider, SimulationEnvironment)

    first = runWithGivenEnvironment(plan, serialized_character_provider.model_dump())
    second = runWithGivenEnvironment(plan, serialized_character_provider.model_dump())

    assert first == second
