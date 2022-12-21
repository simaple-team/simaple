import fastapi
from dependency_injector.wiring import Provide, inject

from simaple.app.application.query import StatisticsResponse, query_statistics
from simaple.app.domain.uow import UnitOfWork
from simaple.app.interface.container import WebContainer

UowProvider = fastapi.Depends(Provide[WebContainer.unit_of_work])

statistics_router = fastapi.APIRouter(prefix="/statistics")


@statistics_router.get("/graph/{simulator_id}", response_model=StatisticsResponse)
@inject
def get_cumulative_graph_data(
    simulator_id: str,
    uow: UnitOfWork = UowProvider,
) -> StatisticsResponse:
    return query_statistics(simulator_id, uow)
