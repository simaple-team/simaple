from simaple.app.application.exception import UnknownSimulatorException
from simaple.app.domain.services.plan import get_simulator_from_plan
from simaple.app.domain.simulator import Simulator
from simaple.app.domain.uow import UnitOfWork
from simaple.simulate.interface.simulator_configuration import SimulatorConfiguration


def create_simulator(conf: SimulatorConfiguration, uow: UnitOfWork) -> str:
    simulator = Simulator.create_from_config(conf)
    uow.simulator_repository().add(simulator)

    return simulator.id


def play_operation(simulator_id: str, dsl: str, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    simulator.dispatch(dsl)
    uow.simulator_repository().update(simulator)


def rollback(simulator_id: str, target_index: int, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    simulator.rollback(target_index)
    uow.simulator_repository().update(simulator)


def run_plan(simulator_id: str, plan: str, uow: UnitOfWork) -> int:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    simulator.rollback(0)

    for dsl in plan.strip().split("\n"):
        if dsl.strip() == "":
            continue

        simulator.dispatch(dsl)

    uow.simulator_repository().update(simulator)
    return simulator.engine.length()


def create_from_plan(plan: str, uow: UnitOfWork) -> str:
    simulator = get_simulator_from_plan(plan)
    uow.simulator_repository().add(simulator)
    return simulator.id
