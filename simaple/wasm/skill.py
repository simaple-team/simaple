from simaple.container.plan_metadata import PlanMetadata
from simaple.container.simulation import get_skill_components
from simaple.simulate.component.base import Component
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.wasm.base import (
    return_js_object_from_pydantic_object,
    wrap_response_by_handling_exception,
)


@return_js_object_from_pydantic_object
@wrap_response_by_handling_exception
def getAllComponent(
    plan: str,
) -> list[Component]:
    plan_metadata_dict, _ = parse_simaple_runtime(plan.strip())

    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)
    if plan_metadata.environment is None or plan_metadata.environment == {}:
        raise ValueError("Environment field is not provided")

    environment = plan_metadata.get_environment()
    skills = get_skill_components(environment)

    return skills
