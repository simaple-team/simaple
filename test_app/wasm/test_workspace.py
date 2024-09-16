from simaple.app.wasm.workspace import (
    createSimulatorFromBaseline,
    createSimulatorFromPlan,
    queryAllSimulator,
    getLatestLogOfSimulator,
    runPlanOnSimulator,
    playOperationOnSimulator,
    getAllLogs,
)


def test_create_simulator_from_baseline(wasm_uow, simulator_configuration):
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {},
            "author": "test",
            "configuration_name": "MinimalCharacterProvider",
            "data": simulator_configuration
        }, wasm_uow)
    assert isinstance(simulator_id, str)


def test_create_simulator_from_plan(wasm_uow):
    simulator_id = createSimulatorFromPlan("""
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
""", wasm_uow)
    assert isinstance(simulator_id, str)


def test_get_all_simulator(wasm_uow, simulator_configuration):
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {},
            "author": "test",
            "configuration_name": "MinimalCharacterProvider",
            "data": simulator_configuration
        }, wasm_uow)

    simulators = queryAllSimulator(wasm_uow)
    assert len(simulators) == 1
    assert simulators[0].id == simulator_id


def test_play_operation(wasm_uow, simulator_configuration):
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {},
            "author": "test",
            "configuration_name": "MinimalCharacterProvider",
            "data": simulator_configuration
        }, wasm_uow)

    op_log = playOperationOnSimulator(
        simulator_id,
        "ELAPSE 100",
        wasm_uow
    )
    assert op_log.dict()



def test_run_plan_on_simulator(wasm_uow, simulator_configuration):
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {},
            "author": "test",
            "configuration_name": "MinimalCharacterProvider",
            "data": simulator_configuration
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


def test_get_latest_log_of_simulator(wasm_uow, simulator_configuration):
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {},
            "author": "test",
            "configuration_name": "MinimalCharacterProvider",
            "data": simulator_configuration
        }, wasm_uow)

    op_log = getLatestLogOfSimulator(simulator_id, wasm_uow)
    assert op_log.model_dump()


def test_get_all_logs(wasm_uow, simulator_configuration):
    simulator_id = createSimulatorFromBaseline({
            "simulation_setting": {},
            "author": "test",
            "configuration_name": "MinimalCharacterProvider",
            "data": simulator_configuration
        }, wasm_uow)

    op_logs = getAllLogs(simulator_id, wasm_uow)
    assert [v.model_dump() for v in op_logs]
