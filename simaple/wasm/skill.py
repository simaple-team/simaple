from simaple.data.jobs.builtin import get_kms_skill_repository
from simaple.spec.spec import Spec
from simaple.wasm.base import (
    return_js_object_from_pydantic_list,
    return_js_object_from_pydantic_object,
)


@return_js_object_from_pydantic_list
def getAllSkillSpec() -> list[Spec]:
    skill_specs = get_kms_skill_repository().get_all()

    return skill_specs


@return_js_object_from_pydantic_object
def getSkillSpec(skill_id: str) -> Spec:
    skill_spec = get_kms_skill_repository().get(id=skill_id)
    if skill_spec is None:
        raise ValueError(f"Skill {skill_id} not found")

    return skill_spec
