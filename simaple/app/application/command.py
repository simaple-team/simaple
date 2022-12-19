from simaple.app.application.exception import UnknownSimulatorException
from simaple.app.domain.history import History
from simaple.app.domain.simulator import Simulator
from simaple.app.domain.simulator_configuration import MinimalSimulatorConfiguration
from simaple.app.domain.uow import UnitOfWork
from simaple.simulate.base import Action


def create_simulator(conf: MinimalSimulatorConfiguration, uow: UnitOfWork) -> str:
    simulator = Simulator.create_from_config(conf)

    playlog = simulator.empty_action_playlog()
    history = History(id=simulator.id, logs=[playlog])

    uow.simulator_repository().add(simulator)
    uow.history_repository().add(history)

    return simulator.id


def play_action(simulator_id: str, action: Action, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)
    history = uow.history_repository().get(simulator_id)

    if history is None or simulator is None:
        raise UnknownSimulatorException()

    playlog = simulator.dispatch(action)
    history.append(playlog)

    uow.history_repository().update(history)
    uow.simulator_repository().update(simulator)


def play_use(simulator_id: str, name: str, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)
    history = uow.history_repository().get(simulator_id)

    if history is None or simulator is None:
        raise UnknownSimulatorException()

    playlog = simulator.dispatch(Action(name=name, method="use", payload=None))
    history.append(playlog)

    uow.history_repository().update(history)
    uow.simulator_repository().update(simulator)


def play_elapse(simulator_id: str, time: float, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)
    history = uow.history_repository().get(simulator_id)

    if history is None or simulator is None:
        raise UnknownSimulatorException()

    playlog = simulator.dispatch(
        Action(
            name="*",
            method="elapse",
            payload=time,
        )
    )
    history.append(playlog)

    uow.history_repository().update(history)
    uow.simulator_repository().update(simulator)


def play_use_and_elapse(simulator_id: str, name: str, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)
    history = uow.history_repository().get(simulator_id)

    if history is None or simulator is None:
        raise UnknownSimulatorException()

    playlog = simulator.dispatch(Action(name=name, method="use", payload=None))
    history.append(playlog)

    playlog = simulator.dispatch(
        Action(name="*", method="elapse", payload=playlog.get_delay())
    )
    history.append(playlog)

    uow.history_repository().update(history)
    uow.simulator_repository().update(simulator)
