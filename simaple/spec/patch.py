from abc import ABCMeta, abstractmethod
from typing import Any, Union

import pydantic
from pydantic import BaseModel


class Patch(BaseModel, metaclass=ABCMeta):
    def apply(self, raw: dict) -> dict:
        ...


class DFSTraversePatch(Patch):
    @abstractmethod
    def patch_list(self, value):
        ...

    @abstractmethod
    def patch_dict(self, k, v):
        ...

    def apply(self, raw: Union[list, dict]) -> Any:
        if isinstance(raw, list):
            return [self.apply(arg) for arg in raw]

        if isinstance(raw, (int, float, str)):
            patch = self.patch_list(raw)
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

    def patch_list(self, value):
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

    def patch_list(self, value):
        return None

    def patch_dict(self, k, v):
        if self.target_keyword in k:
            return {
                k.replace(self.target_keyword, replacement): v
                for replacement in self.extends
            }

        return None
