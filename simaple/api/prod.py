"""
Collection of functions that are used in the WASM interface.

These functions are for Javascript-call only; all methods may
named as camelCase and all arguments maybe pyodide objects.
"""

from typing import Sequence, Type, TypeVar, cast

import pydantic

from simaple.api.base import (
    get_all_component,
    get_initial_plan_from_metadata,
    has_environment,
    provide_environment_augmented_plan,
    run_plan,
    run_plan_with_hint,
)
from simaple.api.models.simulation import OperationLogResponse

BaseModelT = TypeVar("BaseModelT", bound=pydantic.BaseModel)
MaybePyodide = TypeVar("MaybePyodide", pydantic.BaseModel, dict)


def _pyodide_reveal_base_model(
    obj: MaybePyodide, model: Type[BaseModelT]
) -> BaseModelT:
    if isinstance(obj, model):
        return obj

    if isinstance(obj, dict):
        return model.model_validate(obj)

    # assume given object is pyodide object
    dict_obj = cast(dict, obj.to_py())  # type: ignore
    return model.model_validate(dict_obj)


def _pyodide_reveal_base_model_list(
    obj_list: Sequence[MaybePyodide], model: Type[BaseModelT]
) -> list[BaseModelT]:
    if isinstance(obj_list[0], model):
        return obj_list  # type: ignore

    if isinstance(obj_list[0], dict):
        return [model.model_validate(obj) for obj in obj_list]

    # assume given object is pyodide object
    return [model.model_validate(cast(dict, obj.to_py())) for obj in obj_list]  # type: ignore


def runPlan(plan: str) -> list[dict]:
    result = run_plan(plan)
    return [res.model_dump() for res in result]


def hasEnvironment(plan: str) -> bool:
    return has_environment(plan)


def provideEnvironmentAugmentedPlan(plan: str) -> str:
    return provide_environment_augmented_plan(plan)


def getInitialPlanFromMetadata(metadata_dict: dict) -> str:
    metadata_dict = cast(dict, metadata_dict.to_py())  # type: ignore
    return get_initial_plan_from_metadata(metadata_dict)


def runPlanWithHint(
    previous_plan: str, previous_history_dict: list[dict], plan: str
) -> list[dict]:
    previous_history = _pyodide_reveal_base_model_list(
        previous_history_dict, OperationLogResponse
    )
    result = run_plan_with_hint(previous_plan, previous_history, plan)
    return [res.model_dump() for res in result]


def getAllComponent(plan: str) -> list[dict]:
    result = get_all_component(plan)
    return [res.model_dump() for res in result]
