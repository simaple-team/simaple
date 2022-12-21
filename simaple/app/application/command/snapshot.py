from __future__ import annotations

from simaple.app.domain.snapshot import Snapshot
from simaple.app.domain.uow import UnitOfWork


def create_snapshot(simulator_id: str, name: str, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)
    if simulator is None:
        raise KeyError

    snapshot = Snapshot.create_from_simluator(name, simulator)

    uow.snapshot_repository().insert(snapshot)
    uow.commit()


def load_from_snapshot(snapshot_id: str, uow: UnitOfWork) -> str:
    snapshot = uow.snapshot_repository().get(snapshot_id)
    if snapshot is None:
        raise KeyError

    simulator = snapshot.restore_simulator()
    uow.simulator_repository().add(simulator)
    uow.commit()

    return simulator.id
