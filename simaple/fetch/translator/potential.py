import re

import pydantic

from simaple.core.base import AnyStat
from simaple.fetch.translator.base import AbstractStatProvider, NoMatchedStringError
from simaple.gear.potential import Potential


class PotentialTranslator(pydantic.BaseModel):
    patterns: list[tuple[re.Pattern, AbstractStatProvider]]

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def translate(self, expressions: list[str]) -> Potential:
        return Potential(
            options=[self.translate_expression(expr) for expr in expressions]
        )

    def translate_expression(self, expression: str) -> AnyStat:
        for pattern, provider in self.patterns:
            match = pattern.match(expression)
            if match is not None:
                return provider.provide(int(match.group(1) or "0"))

        raise NoMatchedStringError(f"No pattern matched: {expression}")
