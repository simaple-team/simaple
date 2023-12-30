import re

import pydantic

from simaple.core import ExtendedStat
from simaple.fetch.translator.base import AbstractStatProvider, NoMatchedStringError
from simaple.gear.potential import Potential


class PotentialTranslator(pydantic.BaseModel):
    patterns: list[tuple[re.Pattern, AbstractStatProvider]]

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def translate(self, expressions: list[str | None]) -> Potential:
        return Potential(
            options=[
                self._translate_expression(expr)
                for expr in expressions
                if expr is not None
            ]
        )

    def _translate_expression(self, expression: str) -> ExtendedStat:
        for pattern, provider in self.patterns:
            match = pattern.match(expression)
            if match is not None:
                return provider.provide(int(match.group(1) or "0"))

        raise NoMatchedStringError(f"No pattern matched: {expression}")
