from __future__ import annotations

import abc
from typing import Optional

import pydantic


class ComponentSchema(pydantic.BaseModel):
    name: str
    value: dict


class ComponentSchemaRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, name: str) -> Optional[ComponentSchema]:
        ...

    @abc.abstractmethod
    def get_all(self) -> list[ComponentSchema]:
        ...
