from simaple.app.domain.snapshot import SnapshotRepository, Snapshot
from simaple.app.infrastructure.orm import BaseOrm
from sqlalchemy import orm

from sqlalchemy import JSON, Column, DateTime, String
from datetime import datetime
from typing import Optional

from simaple.app.infrastructure.configuration_mapper import ConfigurationMapper


class SnapshotOrm(BaseOrm):
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
        orm = self._to_orm(snapshot)
        self._session.add(orm)
        self._session.flush()

    def get(self, snapshot_id: str) -> Optional[Snapshot]:
        fetched = self._session.query(SnapshotOrm).filter_by(id=snapshot_id).one_or_none()
        if fetched is None:
            return fetched
        
        return self._to_entity(fetched)

    def get_by_name(self, name: str) -> Optional[Snapshot]:
        fetched = self._session.query(SnapshotOrm).filter_by(name=name).one_or_none()
        if fetched is None:
            return fetched
        
        return self._to_entity(fetched)

    def _to_entity(self, orm: SnapshotOrm) -> Snapshot:
        return Snapshot(
            id=orm.id,
            history=orm.history,
            updated_at=orm.updated_at,
            name=orm.name,
            configuration = self._configuration_mapper.load(orm.configuration)
        )

    def _to_orm(self, entity: Snapshot) -> SnapshotOrm:
        return SnapshotOrm(
            id=entity.id,
            history=entity.history,
            updated_at=entity.updated_at,
            name=entity.name,
            configuration = self._configuration_mapper.save(entity.configuration)
        )