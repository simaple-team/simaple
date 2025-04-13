import re
from abc import ABCMeta, abstractmethod
from typing import Any, Union, cast

import pydantic
from pydantic import BaseModel, PrivateAttr

from simaple.spec._math import evaluate_expression


class Patch(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def apply(self, raw, payload: dict | None = None) -> dict:
        """Modify gien raw-dict"""


class DFSTraversePatch(Patch):
    @abstractmethod
    def patch_value(self, value, origin: dict, payload: dict | None = None):
        """Modify gien value in dictionary"""

    @abstractmethod
    def patch_dict(self, k, v, origin: dict, payload: dict | None = None):
        """Modify partial dictionary"""

    def apply(self, raw, payload: dict | None = None) -> dict:
        return cast(dict, self._apply(raw, raw, payload))

    def _apply(self, raw: Union[list, dict], origin: dict, payload: dict | None) -> Any:
        if isinstance(raw, list):
            return [self._apply(arg, origin, payload) for arg in raw]

        if isinstance(raw, (int, float, str)):
            patch = self.patch_value(raw, origin, payload)
            return patch or raw

        interpreted = {}

        excluded_keys = raw.get("exclude", []) + ["exclude"]
        for k, v in raw.items():
            if k in excluded_keys:
                continue
            if isinstance(v, (dict, list)):
                interpreted[k] = self._apply(v, origin, payload)
            else:
                patch = self.patch_dict(k, v, origin, payload)
                if patch is None:
                    interpreted[k] = v
                else:
                    interpreted.update(patch)

        return interpreted


class StringPatch(DFSTraversePatch):
    as_is: list[str]
    to_be: list[str]

    @pydantic.model_validator(mode="after")
    def to_be_and_as_is_must_have_same_length(self):
        if len(self.to_be) != len(self.as_is):
            raise ValueError("As-is and To-be must be same length.")
        return self

    def patch_value(self, value, origin: dict, payload: dict | None = None):
        return self.translate(value)

    def patch_dict(self, k, v, origin: dict, payload: dict | None = None):
        return {self.translate(k): self.translate(v)}

    def translate(
        self, maybe_representation: Union[int, str, float]
    ) -> Union[int, str, float]:
        if not isinstance(maybe_representation, str):
            return maybe_representation

        output = maybe_representation

        for source, target in zip(self.as_is, self.to_be):
            output = output.replace(source, target)

        return output


class KeywordExtendPatch(DFSTraversePatch):
    target_keyword: str
    extends: list[str]

    def patch_value(self, value, origin: dict, payload: dict | None = None):
        return None

    def patch_dict(self, k, v, origin: dict, payload: dict | None = None):
        if self.target_keyword in k:
            return {
                k.replace(self.target_keyword, replacement): v
                for replacement in self.extends
            }

        return None


class ArithmeticPatch(DFSTraversePatch):
    _match_string: re.Pattern = PrivateAttr(default=re.compile(r"^\s*{{(.+)}}\s*$"))
    variables: dict[str, Any]

    def patch_value(self, value, origin: dict, payload: dict | None = None):
        return self.evaluate(value)

    def patch_dict(self, k, v, origin: dict, payload: dict | None = None):
        return {self.evaluate(k): self.evaluate(v)}

    def evaluate(self, value):
        if not isinstance(value, str) or not self._is_target(value):
            return value

        evaluation_target = self._get_evaluation_target(value)
        return self._evaluate_with_math(evaluation_target)

    def _is_target(self, value) -> bool:
        return self._match_string.search(value) is not None

    def _get_evaluation_target(self, value):
        match = self._match_string.search(value)
        if match is None:
            raise ValueError("No evaluation target exists")

        return match.group(1)

    def _evaluate_with_math(self, value):
        return evaluate_expression(value, self.variables)  # pylint: disable=W0123
