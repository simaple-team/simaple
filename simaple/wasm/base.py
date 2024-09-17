"""
Collection of functions that are used in the WASM interface.

These functions are for Javascript-call only; all methods may 
named as camelCase and all arguments maybe pyodide objects.
"""

from functools import wraps
from typing import Any, Callable, TypeVar, cast

import pydantic

BaseModelT = TypeVar("BaseModelT", bound=pydantic.BaseModel)
PyodideJS = TypeVar("PyodideJS")
CallableArgT = TypeVar("CallableArgT", bound=list)


def return_js_object_from_pydantic_list(
    f: Callable[..., list[BaseModelT]]
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
    f: Callable[..., BaseModelT]
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


MaybePyodide = TypeVar("MaybePyodide", dict, Any)


def pyodide_reveal_dict(obj: MaybePyodide) -> dict:
    if isinstance(obj, dict):
        return obj

    # assume given object is pyodide object
    return cast(dict, obj.to_py())
