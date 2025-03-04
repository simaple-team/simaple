from typing import Any, Optional, Sequence

import pydantic
from typing_extensions import TypedDict

from simaple.spec.patch import Patch


class SpecMetadata(pydantic.BaseModel):
    label: dict[str, Any] = pydantic.Field(default_factory=dict)
    annotation: dict[str, Any] = pydantic.Field(default_factory=dict)

    def matches(self, **labels) -> bool:
        return all(self.label.get(k) == v for k, v in labels.items())


class PatchSpecificationMatchFailError(Exception):
    ...


class PatchArgument(TypedDict):
    name: str
    payload: dict[str, Any] | None


class Spec(pydantic.BaseModel):
    kind: str
    version: str
    metadata: SpecMetadata
    data: dict[str, Any]
    patch: Optional[list[str | PatchArgument]] = None
    ignore_overflowing_patch: bool = True

    def get_classname(self):
        return self.version.split("/")[1]

    def get_patch_arguments(self) -> list[PatchArgument]:
        if self.patch is None:
            return []

        return [
            {"name": arg, "payload": None} if isinstance(arg, str) else arg
            for arg in self.patch
        ]

    def is_patch_fits(self, patches: Optional[Sequence[Patch]] = None) -> bool:
        if self.patch is None:
            return patches is None

        if patches is None:
            return False

        if len(patches) != len(self.patch):
            return False

        return all(
            given.__class__.__name__ == expected["name"]
            for given, expected in zip(patches, self.get_patch_arguments())
        )

    def _is_patch_fits_with_overflow(
        self, patches: Optional[Sequence[Patch]] = None
    ) -> tuple[bool, list[tuple[Patch, PatchArgument]]]:
        if self.patch is None:
            return True, []

        if patches is None:
            return False, []

        aligned_patches = []

        my_patch_ptr, given_patch_ptr = 0, 0

        patch_arguments = self.get_patch_arguments()

        while my_patch_ptr < len(patch_arguments) and given_patch_ptr < len(patches):
            if (
                patches[given_patch_ptr].__class__.__name__
                == patch_arguments[my_patch_ptr]["name"]
            ):
                aligned_patches.append(
                    (patches[given_patch_ptr], patch_arguments[my_patch_ptr])
                )
                my_patch_ptr += 1
            given_patch_ptr += 1

        return my_patch_ptr == len(patch_arguments), aligned_patches

    def interpret(self, patches: Optional[Sequence[Patch]] = None):
        data = self.data.copy()
        if patches is None:
            return data

        if self.ignore_overflowing_patch:
            fits, aligned_patches = self._is_patch_fits_with_overflow(patches)
            if not fits:
                raise PatchSpecificationMatchFailError()
        else:
            if not self.is_patch_fits(patches):
                raise PatchSpecificationMatchFailError()
            aligned_patches = [
                (patch, patch_argument)
                for patch, patch_argument in zip(patches, self.get_patch_arguments())
            ]

        for patch, patch_argument in aligned_patches:
            data = patch.apply(data, patch_argument["payload"])

        return data
