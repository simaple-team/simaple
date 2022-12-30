import fastapi
from dependency_injector.wiring import Provide, inject

from simaple.app.application.query.component_spec import query_all_component_schemas
from simaple.app.domain.component_schema import ComponentSchema
from simaple.app.domain.uow import UnitOfWork
from simaple.app.interface.container import WebContainer

UowProvider = fastapi.Depends(Provide[WebContainer.unit_of_work])

component_spec_router = fastapi.APIRouter(prefix="/component_spec")


@component_spec_router.get("/")
@inject
def get_all_component_spec(
    uow: UnitOfWork = UowProvider,
) -> dict[str, ComponentSchema]:
    return query_all_component_schemas(uow)
