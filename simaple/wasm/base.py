"""
Collection of functions that are used in the WASM interface.

These functions are for Javascript-call only; all methods may
named as camelCase and all arguments maybe pyodide objects.
"""

from functools import wraps
from typing import Callable, Sequence, Type, TypeVar, cast

import pydantic

BaseModelT = TypeVar("BaseModelT", bound=pydantic.BaseModel)
PyodideJS = TypeVar("PyodideJS")
CallableArgT = TypeVar("CallableArgT", bound=list)


def return_js_object_from_pydantic_list(
    f: Callable[..., list[BaseModelT]],
) -> Callable[..., list[BaseModelT]]:
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


def return_js_object_from_pydantic_object(
    f: Callable[..., BaseModelT],
) -> Callable[..., BaseModelT]:
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            from js import Object  # type: ignore
            from pyodide.ffi import to_js  # type: ignore

            result = f(*args, **kwargs)
            return to_js(result.model_dump(), dict_converter=Object.fromEntries)
        except ImportError:
            return f(*args, **kwargs)

    return wrapper


MaybePyodide = TypeVar("MaybePyodide", pydantic.BaseModel, dict)


def pyodide_reveal_base_model(obj: MaybePyodide, model: Type[BaseModelT]) -> BaseModelT:
    if isinstance(obj, model):
        return obj

    # assume given object is pyodide object
    dict_obj = cast(dict, obj.to_py())  # type: ignore
    return model.model_validate(dict_obj)


def pyodide_reveal_base_model_list(
    obj_list: Sequence[MaybePyodide], model: Type[BaseModelT]
) -> list[BaseModelT]:
    if isinstance(obj_list[0], model):
        return obj_list  # type: ignore

    # assume given object is pyodide object
    return [model.model_validate(cast(dict, obj.to_py())) for obj in obj_list]  # type: ignore
