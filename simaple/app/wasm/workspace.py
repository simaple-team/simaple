from simaple.app.application.command.simulator import (
    create_from_plan,
    create_simulator,
    play_operation,
    rollback,
    run_plan,
)
from simaple.app.application.query import (
    OperationLogResponse,
    SimulatorResponse,
    query_all_simulator,
    query_every_opration_log,
    query_latest_operation_log,
    query_operation_log,
)
from simaple.app.wasm.base import (
    MaybePyodide,
    SessionlessUnitOfWork,
    pyodide_reveal_dict,
    return_js_object_from_pydantic_list,
    return_js_object_from_pydantic_object,
)
from simaple.simulate.interface.simulator_configuration import (
    BaselineConfiguration,
    MinimalSimulatorConfiguration,
)


def createSimulatorFromMinimalConf(
    conf: MaybePyodide,
    uow: SessionlessUnitOfWork,
):
    baseline_conf = MinimalSimulatorConfiguration.model_validate(
        pyodide_reveal_dict(conf)
    )
    simulator_id = create_simulator(baseline_conf, uow)
    return simulator_id


def createSimulatorFromBaseline(
    conf: MaybePyodide,
    uow: SessionlessUnitOfWork,
) -> str:
    baseline_conf = BaselineConfiguration.model_validate(pyodide_reveal_dict(conf))
    simulator_id = create_simulator(baseline_conf, uow)
    return simulator_id


def createSimulatorFromPlan(
    plan: str,
    uow: SessionlessUnitOfWork,
) -> str:
    simulator_id = create_from_plan(plan, uow)

    return simulator_id


@return_js_object_from_pydantic_list
def queryAllSimulator(
    uow: SessionlessUnitOfWork,
) -> list[SimulatorResponse]:
    return query_all_simulator(uow)


@return_js_object_from_pydantic_object
def playOperationOnSimulator(
    simulator_id: str, operation: str, uow: SessionlessUnitOfWork
) -> OperationLogResponse:
    play_operation(simulator_id, operation, uow)

    return query_latest_operation_log(simulator_id, uow)


@return_js_object_from_pydantic_list
def runPlanOnSimulator(
    simulator_id: str,
    plan: str,
    uow: SessionlessUnitOfWork,
) -> list[OperationLogResponse]:
    run_plan(simulator_id, plan, uow)

    return query_every_opration_log(simulator_id, uow)


@return_js_object_from_pydantic_object
def getLatestLogOfSimulator(
    simulator_id: str,
    uow: SessionlessUnitOfWork,
) -> OperationLogResponse:
    return query_operation_log(simulator_id, -1, uow)


@return_js_object_from_pydantic_list
def getAllLogs(
    simulator_id: str,
    uow: SessionlessUnitOfWork,
) -> list[OperationLogResponse]:
    return query_every_opration_log(simulator_id, uow)


def rollbackToCheckpoint(
    simulator_id: str,
    history_index: int,
    uow: SessionlessUnitOfWork,
) -> None:
    rollback(simulator_id, history_index, uow)

    return
