import re
from abc import ABCMeta, abstractmethod

import pydantic

from simaple.core.base import AnyStat
from simaple.gear.potential import Potential


class NoMatchedStringError(Exception):
    ...


class ItemElementTranslator:
    ...


class AbstractStatProvider(pydantic.BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def provide(self, dependency: int) -> AnyStat:
        ...


class PotentialTranslator(pydantic.BaseModel):
    patterns: list[tuple[re.Pattern, AbstractStatProvider]]

    class Config:
        arbitrary_types_allowed = True

    def translate(self, expressions: list[str]) -> Potential:
        return Potential(
            options=[self.translate_expression(expr) for expr in expressions]
        )

    def translate_expression(self, expression: str):
        for pattern, provider in self.patterns:
            match = pattern.match(expression)
            if match is not None:
                return provider.provide(match.group(1))

        raise NoMatchedStringError("No pattern matched")
