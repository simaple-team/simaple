from simaple.app.application.exception import (
    ApplicationError,
    UnknownSimulatorException,
)
from simaple.app.domain.simulator import Simulator
from simaple.app.domain.simulator_configuration import SimulatorConfiguration
from simaple.app.domain.uow import UnitOfWork
from simaple.simulate.base import Action


def create_simulator(conf: SimulatorConfiguration, uow: UnitOfWork) -> str:
    simulator = Simulator.create_from_config(conf)
    uow.simulator_repository().add(simulator)

    return simulator.id


def play_action(simulator_id: str, action: Action, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    simulator.dispatch(action)
    uow.simulator_repository().update(simulator)


def play_use(simulator_id: str, name: str, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    simulator.dispatch(Action(name=name, method="use", payload=None))
    uow.simulator_repository().update(simulator)


def play_elapse(simulator_id: str, time: float, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    simulator.dispatch(
        Action(
            name="*",
            method="elapse",
            payload=time,
        )
    )
    uow.simulator_repository().update(simulator)


def play_use_and_elapse(simulator_id: str, name: str, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    simulator.dispatch(Action(name=name, method="use", payload=None))
    simulator.dispatch(
        Action(
            name="*",
            method="elapse",
            payload=simulator.history.get_latest_playlog().get_delay(),
        )
    )

    uow.simulator_repository().update(simulator)


def rollback(simulator_id: str, target_index: int, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    simulator.rollback(target_index)
    uow.simulator_repository().update(simulator)


def override_checkpint(simulator_id, checkpoint: dict, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    if len(simulator.history) != 1:
        raise ApplicationError("override_checkpoint only valid for no-history")

    simulator.change_current_checkpoint(checkpoint)
    uow.simulator_repository().update(simulator)
