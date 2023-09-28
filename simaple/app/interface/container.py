import pydantic
import sqlalchemy
from dependency_injector import containers, providers
from sqlalchemy.orm import sessionmaker

from simaple.app.infrastructure.component_schema_repository import (
    LoadableComponentSchemaRepository,
)
from simaple.app.infrastructure.orm import BaseOrm
from simaple.app.infrastructure.repository import InmemorySimulatorRepository
from simaple.app.infrastructure.uow import SimpleUnitOfWork
from simaple.data.skill import get_kms_spec_resource_path
from simaple.spec.repository import DirectorySpecRepository


class WebSetting(pydantic.BaseModel):
    sqlite_url: str = "sqlite:///.sqlite.db"
    spec_file_path: str = pydantic.Field(default_factory=get_kms_spec_resource_path)


class SqlDatabase:
    def __init__(self, url):
        self._engine = sqlalchemy.create_engine(
            url, encoding="utf8", connect_args={"check_same_thread": False}
        )

    def create(self):
        BaseOrm.metadata.create_all(self._engine)

    def delete(self):
        BaseOrm.metadata.drop_all(self._engine)

    def get_session_builder(self):
        return sessionmaker(bind=self._engine)


class WebContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    simulator_repository = providers.Singleton(InmemorySimulatorRepository)

    sql_database = providers.Singleton(SqlDatabase, config.sqlite_url)

    component_schema_repository = providers.Singleton(LoadableComponentSchemaRepository)

    spec_repository = providers.Singleton(
        DirectorySpecRepository, config.spec_file_path
    )

    unit_of_work = providers.Factory(
        SimpleUnitOfWork,
        sql_database.provided.get_session_builder.call(),
        simulator_repository,
        component_schema_repository,
        spec_repository,
    )
