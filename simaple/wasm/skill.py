from simaple.spec.spec import Spec
from simaple.wasm.base import (
    return_js_object_from_pydantic_list,
    return_js_object_from_pydantic_object,
)
from simaple.wasm.globals import get_internal_database


@return_js_object_from_pydantic_list
def getAllSkillSpec() -> list[Spec]:
    internal_database = get_internal_database()
    skill_specs = internal_database.spec_repository().get_all()

    return skill_specs


@return_js_object_from_pydantic_object
def getSkillSpec(skill_id: str) -> Spec:
    internal_database = get_internal_database()
    skill_spec = internal_database.spec_repository().get(id=skill_id)
    if skill_spec is None:
        raise ValueError(f"Skill {skill_id} not found")

    return skill_spec
