import fastapi
import pydantic
from fastapi import Depends

from simaple.app.services.base import get_logs, get_play_logs
from simaple.app.services.statistics import get_cumulative_logs, get_damage_logs

statistics_router = fastapi.APIRouter(prefix="/statistics")


class StatisticsResponse(pydantic.BaseModel):
    cumulative_x: list[float]
    cumulative_y: list[float]
    value_x: list[float]
    value_y: list[float]


@statistics_router.get("/graph/{workspace_id}", response_model=StatisticsResponse)
def get_cumulative_graph_data(
    workspace_id: str,
    logs=Depends(get_logs),
) -> StatisticsResponse:
    play_logs = get_play_logs(workspace_id, logs)

    cumulative_x, cumulative_y = get_cumulative_logs(play_logs)
    value_x, value_y = get_damage_logs(play_logs)

    return StatisticsResponse(
        cumulative_x=cumulative_x,
        cumulative_y=cumulative_y,
        value_x=value_x,
        value_y=value_y,
    )
