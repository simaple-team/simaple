from simaple.app.application.query.skill import get_all_skill, get_skill
from simaple.app.wasm.base import (
    SessionlessUnitOfWork,
    return_js_object_from_pydantic_list,
    return_js_object_from_pydantic_object,
)
from simaple.spec.spec import Spec


@return_js_object_from_pydantic_list
def getAllSkillSpec(
    uow: SessionlessUnitOfWork,
) -> list[Spec]:
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
