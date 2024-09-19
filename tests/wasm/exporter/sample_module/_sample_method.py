from pydantic import BaseModel


class A(BaseModel):
    x: int
    y: int


class B(BaseModel):
    x: int
    z: int


class C(BaseModel):
    x: int
    y: int
    z: int


def func_str_to_none(x: str) -> None:
    return


def func_str_to_pydantic(x: str) -> A:
    return A(x=1, y=2)


def func_str_and_dict_to_pydantic(x: str, y: dict) -> B:
    return B(x=1, z=2)


def func_str_to_pydantic_list(x: str) -> list[A]:
    return [A(x=1, y=2), A(x=3, y=4)]


def func_str_to_pydantic_tuple(x: str) -> tuple[A, C]:
    return A(x=1, y=2), C(x=3, y=0, z=4)
