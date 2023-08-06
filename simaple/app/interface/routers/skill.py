import fastapi
from dependency_injector.wiring import inject

from simaple.app.application.query.skill import get_all_skill, get_skill
from simaple.app.domain.uow import UnitOfWork
from simaple.app.interface.routers.base import UowProvider
from simaple.spec.spec import Spec

skill_router = fastapi.APIRouter(prefix="/skills")


@skill_router.get("/")
@inject
def get_all_skill_spec(
    uow: UnitOfWork = UowProvider,
) -> list[Spec]:
    skill_specs = get_all_skill(uow)

    return skill_specs


@skill_router.get("/{skill_id}")
@inject
def get_skill_spec(
    skill_id: str,
    uow: UnitOfWork = UowProvider,
) -> Spec:
    skill_spec = get_skill(uow, skill_id)
    if skill_spec is None:
        raise fastapi.HTTPException(status_code=404, detail="Skill not found")

    return skill_spec
