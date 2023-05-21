import fastapi
from dependency_injector.wiring import inject

from simaple.app.application.query.skill import get_skill
from simaple.app.domain.uow import UnitOfWork
from simaple.app.interface.routers.base import UowProvider
from simaple.spec.spec import Spec

skill_router = fastapi.APIRouter(prefix="/skill")


@skill_router.get("/{skill_id}")
@inject
def get_all_component_spec(
    skill_id: str,
    uow: UnitOfWork = UowProvider,
) -> Spec:
    skill_spec = get_skill(uow, skill_id)
    if skill_spec is None:
        raise fastapi.HTTPException(status_code=404, detail="Skill not found")

    return skill_spec
