from simaple.app.wasm.base import MaybePyodide, SessionlessUnitOfWork, pyodide_reveal_dict, return_js_object_from_pydantic_list, return_js_object_from_pydantic_object
from simaple.simulate.interface.simulator_configuration import BaselineConfiguration, MinimalSimulatorConfiguration

from simaple.app.application.command.simulator import (
    create_simulator,
)
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


def createSimulatorFromMinimalConf(
    conf: MaybePyodide,
    uow: SessionlessUnitOfWork,
):
    baseline_conf = MinimalSimulatorConfiguration.model_validate(pyodide_reveal_dict(conf))
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
def getAllSimulator(
    uow: SessionlessUnitOfWork,
) -> list[SimulatorResponse]:
    return query_all_simulator(uow)


@return_js_object_from_pydantic_object
def playOperation(
    simulator_id: str,
    operation: str,
    uow: SessionlessUnitOfWork
) -> OperationLogResponse:
    play_operation(simulator_id, operation, uow)

    return query_latest_operation_log(simulator_id, uow)
