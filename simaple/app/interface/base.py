from simaple.app.infrastructure.repository import (
    InmemoryHistoryRepository,
    InmemorySimulatorRepository,
)
from simaple.app.infrastructure.uow import SimpleUnitOfWork
import os
import sqlalchemy

from sqlalchemy.orm import sessionmaker
from simaple.app.infrastructure.orm import BaseOrm

_simulator_repository = InmemorySimulatorRepository()

sqlite_file_name = ".sqlite.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = sqlalchemy.create_engine(
    sqlite_url,
    encoding="utf8",
)

if not os.path.exists(sqlite_file_name):
    BaseOrm.metadata.create_all(engine)


def get_unit_of_work():
    return SimpleUnitOfWork(
        sessionmaker(bind=engine),
        _simulator_repository,
    )
