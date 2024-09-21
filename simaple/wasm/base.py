"""
Collection of functions that are used in the WASM interface.

These functions are for Javascript-call only; all methods may
named as camelCase and all arguments maybe pyodide objects.
"""

from functools import wraps
from typing import Callable, Generic, Literal, Type, TypeVar, cast

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


T = TypeVar("T")


class SuccessResponse(pydantic.BaseModel, Generic[T]):
    model_config = pydantic.ConfigDict(extra="forbid")

    success: Literal[True]
    data: T


class ErrorResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    success: Literal[False]
    message: str


def wrap_response_by_handling_exception(
    f: Callable[..., T],
) -> Callable[..., SuccessResponse[T] | ErrorResponse]:
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return SuccessResponse(success=True, data=f(*args, **kwargs))
        except Exception as e:
            return ErrorResponse(success=False, message=str(e))

    return wrapper


MaybePyodide = TypeVar("MaybePyodide", pydantic.BaseModel, dict)


def pyodide_reveal_base_model(obj: MaybePyodide, model: Type[BaseModelT]) -> BaseModelT:
    if isinstance(obj, model):
        return obj

    # assume given object is pyodide object
    dict_obj = cast(dict, obj.to_py())  # type: ignore
    return model.model_validate(dict_obj)
