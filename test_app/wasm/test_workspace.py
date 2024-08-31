from simaple.app.wasm.workspace import (
    createSimulatorFromBaseline,
    createSimulatorFromPlan,
    createSimulatorFromMinimalConf,
    getAllSimulator,
    getLatestLogOfSimulator,
    runPlanOnSimulator,
    playOperationOnSimulator,
)


def test_create_simulator_from_baseline(wasm_uow):
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {
                "tier": "Legendary",
                "jobtype": "archmagetc",
                "job_category": 1,
                "level": 280,
                "passive_skill_level": 0,
                "combat_orders_level": 1,
                "artifact_level": 40
            }
        }, wasm_uow)
    assert isinstance(simulator_id, str)


def test_create_simulator_from_minimal_conf(wasm_uow):
    simulator_id = createSimulatorFromMinimalConf({
            "job": "archmagetc",
            "character_stat": {
                "STR": 1105.0,
                "LUK": 2650.0,
                "INT": 4963.0,
                "DEX": 1030.0,
                "STR_multiplier": 90.0,
                "LUK_multiplier": 90.0,
                "INT_multiplier": 709.0,
                "DEX_multiplier": 90.0,
                "STR_static": 470.0,
                "LUK_static": 610.0,
                "INT_static": 16530.0,
                "DEX_static": 310.0,
                "attack_power": 1682.0,
                "magic_attack": 2421.8,
                "magic_attack_multiplier": 93.0,
                "critical_rate": 50.0,
                "critical_damage": 76.0,
                "boss_damage_multiplier": 296.0,
                "damage_multiplier": 93.7,
                "ignored_defence": 95.66920732826136,
                "MHP": 26530.0,
                "MMP": 15335.0,
                "MHP_multiplier": 5.0,
                "MMP_multiplier": 6.0
            },
            "action_stat": {
                "cooltime_reduce": 0.0,
                "summon_duration": 10.0,
                "buff_duration": 60.0,
                "cooltime_reduce_rate": 0.0
            },
            "character_level": 280,
        }, wasm_uow)
    assert isinstance(simulator_id, str)


def test_create_simulator_from_plan(wasm_uow):
    simulator_id = createSimulatorFromPlan("""
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

""", wasm_uow)
    assert isinstance(simulator_id, str)


def test_get_all_simulator(wasm_uow):
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {
                "tier": "Legendary",
                "jobtype": "archmagetc",
                "job_category": 1,
                "level": 280,
                "passive_skill_level": 0,
                "combat_orders_level": 1,
                "artifact_level": 40
            }
        }, wasm_uow)

    simulators = getAllSimulator(wasm_uow)
    assert len(simulators) == 1
    assert simulators[0].id == simulator_id


def test_play_operation(wasm_uow):
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {
                "tier": "Legendary",
                "jobtype": "archmagetc",
                "job_category": 1,
                "level": 280,
                "passive_skill_level": 0,
                "combat_orders_level": 1,
                "artifact_level": 40
            }
        }, wasm_uow)
    op_log = playOperationOnSimulator(
        simulator_id,
        "ELAPSE 100",
        wasm_uow
    )
    assert op_log.dict()



def test_run_plan_on_simulator(wasm_uow):
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {
                "tier": "Legendary",
                "jobtype": "archmagetc",
                "job_category": 1,
                "level": 280,
                "passive_skill_level": 0,
                "combat_orders_level": 1,
                "artifact_level": 40
            }
        }, wasm_uow)
    op_logs = runPlanOnSimulator(
        simulator_id,
"""
USE "플레임 스윕" 200.0
CAST "플레임 스윕"
ELAPSE 200.0""",
        wasm_uow
    )
    assert [v.model_dump() for v in op_logs]


def test_get_latest_log_of_simulator(wasm_uow):
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {
                "tier": "Legendary",
                "jobtype": "archmagetc",
                "job_category": 1,
                "level": 280,
                "passive_skill_level": 0,
                "combat_orders_level": 1,
                "artifact_level": 40
            }
        }, wasm_uow)

    op_log = getLatestLogOfSimulator(simulator_id, wasm_uow)
    assert op_log.model_dump()
