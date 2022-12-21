from __future__ import annotations

from datetime import datetime

import pydantic

from simaple.app.domain.snapshot import Snapshot
from simaple.app.domain.uow import UnitOfWork


class SnapshotResponse(pydantic.BaseModel):
    id: str
    length: int
    updated_at: datetime
    name: str
    configuration_name: str

    @classmethod
    def from_snapshot(cls, snapshot: Snapshot) -> SnapshotResponse:
        return SnapshotResponse(
            id=snapshot.id,
            length=len(snapshot.history),
            updated_at=snapshot.updated_at,
            name=snapshot.name,
            configuration_name=snapshot.configuration.get_name(),
        )


def query_all_snapshot(uow: UnitOfWork) -> list[SnapshotResponse]:
    snapshots = uow.snapshot_repository().get_all()
    return [SnapshotResponse.from_snapshot(snapshot) for snapshot in snapshots]
