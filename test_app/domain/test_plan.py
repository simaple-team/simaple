from simaple.app.domain.services.plan import get_simulator_from_plan

def test_run_plan():
    get_simulator_from_plan("""
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
    """)
