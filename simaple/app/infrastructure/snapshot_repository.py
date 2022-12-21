from datetime import datetime
from typing import Optional, cast

from sqlalchemy import JSON, Column, DateTime, String, orm

from simaple.app.domain.snapshot import Snapshot, SnapshotRepository
from simaple.app.infrastructure.configuration_mapper import ConfigurationMapper
from simaple.app.infrastructure.orm import BaseOrm


class SnapshotOrm(BaseOrm):  # type: ignore
    __tablename__ = "snapshot"

    id = Column(String(256), primary_key=True)
    history = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, nullable=False)
    name = Column(String(128), nullable=False)
    configuration = Column(JSON, nullable=False)


class SqlSnapshotRepository(SnapshotRepository):
    def __init__(self, session: orm.Session):
        self._session = session
        self._configuration_mapper = ConfigurationMapper()

    def insert(self, snapshot: Snapshot) -> None:
        snapshot_orm = self._to_orm(snapshot)
        self._session.add(snapshot_orm)
        self._session.flush()

    def get_all(self) -> list[Snapshot]:
        fetched = self._session.query(SnapshotOrm)

        return [self._to_entity(snapshot_orm) for snapshot_orm in fetched]

    def get(self, snapshot_id: str) -> Optional[Snapshot]:
        fetched = (
            self._session.query(SnapshotOrm).filter_by(id=snapshot_id).one_or_none()
        )
        if fetched is None:
            return fetched

        return self._to_entity(fetched)

    def get_by_name(self, name: str) -> Optional[Snapshot]:
        fetched = self._session.query(SnapshotOrm).filter_by(name=name).one_or_none()
        if fetched is None:
            return fetched

        return self._to_entity(fetched)

    def _to_entity(self, snapshot_orm: SnapshotOrm) -> Snapshot:
        return Snapshot(
            id=snapshot_orm.id,
            history=snapshot_orm.history,
            updated_at=snapshot_orm.updated_at,
            name=snapshot_orm.name,
            configuration=self._configuration_mapper.load(
                cast(dict, snapshot_orm.configuration)
            ),
        )

    def _to_orm(self, entity: Snapshot) -> SnapshotOrm:
        return SnapshotOrm(
            id=entity.id,
            history=entity.history.dict(),
            updated_at=entity.updated_at,
            name=entity.name,
            configuration=self._configuration_mapper.dump(entity.configuration),
        )
