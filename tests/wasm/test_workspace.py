from simaple.wasm.workspace import getSerializedCharacterProvider, run


def test_get_serialized_character_provider_then_run():
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
    serialized_character_provider = getSerializedCharacterProvider(plan)
    assert isinstance(serialized_character_provider, dict)

    first = run(plan, serialized_character_provider)
    second = run(plan, serialized_character_provider)

    assert first == second
