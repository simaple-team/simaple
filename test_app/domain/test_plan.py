from simaple.app.domain.services.plan import get_simulator_from_plan

def test_run_plan():
    get_simulator_from_plan("""
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
    """)
