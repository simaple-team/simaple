from simaple.app.application.query.skill import get_all_skill, get_skill
from simaple.app.domain.uow import UnitOfWork
from simaple.app.interface.routers.base import UowProvider
from simaple.spec.spec import Spec
from simaple.app.wasm.base import (
    MaybePyodide,
    SessionlessUnitOfWork,
    pyodide_reveal_dict,
    return_js_object_from_pydantic_list,
    return_js_object_from_pydantic_object,
)

@return_js_object_from_pydantic_list
def getAllSkillSpec(
    uow: SessionlessUnitOfWork,
):
    skill_specs = get_all_skill(uow)
    return skill_specs


@return_js_object_from_pydantic_object
def getSkillSpec(
    skill_id: str,
    uow: SessionlessUnitOfWork,
) -> Spec:
    skill_spec = get_skill(uow, skill_id)
    if skill_spec is None:
        raise ValueError("Skill not found")

    return skill_spec
