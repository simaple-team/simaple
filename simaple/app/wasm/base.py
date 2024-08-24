from simaple.app.application.command.simulator import create_from_plan
from simaple.app.application.query import OperationLogResponse, query_every_opration_log
from simaple.app.infrastructure.component_schema_repository import (
    LoadableComponentSchemaRepository,
)
from simaple.app.infrastructure.inmemory import (
    InmemorySnapshotRepository,
    SessionlessUnitOfWork,
)
from simaple.app.infrastructure.repository import InmemorySimulatorRepository
from simaple.data.skill import get_kms_spec_resource_path
from simaple.spec.repository import DirectorySpecRepository


def create_uow() -> SessionlessUnitOfWork:
    return SessionlessUnitOfWork(
        simulator_repository=InmemorySimulatorRepository(),
        component_schema_repository=LoadableComponentSchemaRepository(),
        spec_repository=DirectorySpecRepository(get_kms_spec_resource_path()),
        snapshot_repository=InmemorySnapshotRepository(),
    )


def run_plan(plan: str, uow: SessionlessUnitOfWork) -> list[OperationLogResponse]:
    simulator_id = create_from_plan(plan, uow)
    return query_every_opration_log(simulator_id, uow)
