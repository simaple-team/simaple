import math
import re
from abc import ABCMeta, abstractmethod
from typing import Any, Union

import pydantic
from pydantic import BaseModel, PrivateAttr


class Patch(BaseModel, metaclass=ABCMeta):
    def apply(self, raw: dict) -> dict:
        ...


class DFSTraversePatch(Patch):
    @abstractmethod
    def patch_value(self, value):
        ...

    @abstractmethod
    def patch_dict(self, k, v):
        ...

    def apply(self, raw: Union[list, dict]) -> Any:
        if isinstance(raw, list):
            return [self.apply(arg) for arg in raw]

        if isinstance(raw, (int, float, str)):
            patch = self.patch_value(raw)
            return patch or raw

        interpreted = {}

        excluded_keys = raw.get("exclude", []) + ["exclude"]
        for k, v in raw.items():
            if k in excluded_keys:
                continue
            if isinstance(v, (dict, list)):
                interpreted[k] = self.apply(v)
            else:
                patch = self.patch_dict(k, v)
                if patch is None:
                    interpreted[k] = v
                else:
                    interpreted.update(patch)

        return interpreted


class StringPatch(DFSTraversePatch):
    as_is: list[str]
    to_be: list[str]

    @pydantic.validator("to_be")
    @classmethod
    def to_be_and_as_is_must_have_same_length(cls, v, values, **kwargs):
        if len(v) != len(values["as_is"]):
            raise ValueError("As-is and To-be must be same length.")
        return v

    def patch_value(self, value):
        return self.translate(value)

    def patch_dict(self, k, v):
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

    def patch_value(self, value):
        return None

    def patch_dict(self, k, v):
        if self.target_keyword in k:
            return {
                k.replace(self.target_keyword, replacement): v
                for replacement in self.extends
            }

        return None


class EvalPatch(DFSTraversePatch):
    _match_string: re.Pattern = PrivateAttr(default=re.compile(r"^\s*{{(.+)}}\s*$"))
    injected_values: dict[str, Any]

    def patch_value(self, value):
        return self.evaluate(value)

    def patch_dict(self, k, v):
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
        global_variables = globals()
        global_variables.update(self.injected_values)
        global_variables["math"] = math

        assert "import" not in value
        return eval(value, global_variables)  # pylint: disable=W0123
