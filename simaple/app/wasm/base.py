"""
Collection of functions that are used in the WASM interface.

These functions are for Javascript-call only; all methods may 
named as camelCase and all arguments maybe pyodide objects.
"""

from functools import wraps
from typing import Any, Callable, TypeVar, cast

import pydantic

from simaple.app.application.command.simulator import (
    create_from_plan,
    create_simulator,
    run_plan,
)
from simaple.app.application.query import OperationLogResponse, query_every_opration_log
from simaple.app.infrastructure.component_schema_repository import (
    LoadableComponentSchemaRepository,
)
from simaple.app.infrastructure.inmemory import (
    InmemorySnapshotRepository,
    SessionlessUnitOfWork,
)
from simaple.app.infrastructure.repository import InmemorySimulatorRepository
from simaple.data.skill import get_kms_spec_resource_path
from simaple.simulate.interface.simulator_configuration import BaselineConfiguration
from simaple.spec.repository import DirectorySpecRepository

BaseModelT = TypeVar("BaseModelT", bound=pydantic.BaseModel)


def return_js_object_from_pydantic_list(f: Callable[..., list[BaseModelT]]) -> Any:
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            from js import Object  # type: ignore
            from pyodide.ffi import to_js  # type: ignore

            result = f(*args, **kwargs)
            return to_js(
                [v.model_dump() for v in result], dict_converter=Object.fromEntries
            )
        except ImportError:
            return f(*args, **kwargs)

    return wrapper


MaybePyodide = TypeVar("MaybePyodide", dict, Any)


def _pyodide_reveal_dict(obj: MaybePyodide) -> dict:
    if isinstance(obj, dict):
        return obj

    # assume given object is pyodide object
    return cast(dict, obj.to_py())


def createUow() -> SessionlessUnitOfWork:
    return SessionlessUnitOfWork(
        simulator_repository=InmemorySimulatorRepository(),
        component_schema_repository=LoadableComponentSchemaRepository(),
        spec_repository=DirectorySpecRepository(get_kms_spec_resource_path()),
        snapshot_repository=InmemorySnapshotRepository(),
    )


def createSimulatorFromBaseline(
    conf: MaybePyodide,
    uow: SessionlessUnitOfWork,
) -> str:
    baseline_conf = BaselineConfiguration.model_validate(_pyodide_reveal_dict(conf))
    simulator_id = create_simulator(baseline_conf, uow)
    return simulator_id


@return_js_object_from_pydantic_list
def runSimulatorWithPlan(
    simulator_id: str,
    plan: str,
    uow: SessionlessUnitOfWork,
) -> list[OperationLogResponse]:
    _ = run_plan(simulator_id, plan, uow)

    return query_every_opration_log(simulator_id, uow)


@return_js_object_from_pydantic_list
def runSimulatorWithPlanConfig(
    plan: str, uow: SessionlessUnitOfWork
) -> list[OperationLogResponse]:
    simulator_id = create_from_plan(plan, uow)
    return query_every_opration_log(simulator_id, uow)
