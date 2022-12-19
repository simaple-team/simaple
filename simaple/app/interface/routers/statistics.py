import fastapi
from fastapi import Depends

from simaple.app.application.query import StatisticsResponse, query_statistics
from simaple.app.domain.uow import UnitOfWork
from simaple.app.interface.base import get_unit_of_work

statistics_router = fastapi.APIRouter(prefix="/statistics")


@statistics_router.get("/graph/{simulator_id}", response_model=StatisticsResponse)
def get_cumulative_graph_data(
    simulator_id: str,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> StatisticsResponse:
    return query_statistics(simulator_id, uow)
