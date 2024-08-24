from typing import Any, Optional, Sequence

import pydantic

from simaple.spec.patch import Patch


class SpecMetadata(pydantic.BaseModel):
    label: dict[str, Any] = pydantic.Field(default_factory=dict)
    annotation: dict[str, Any] = pydantic.Field(default_factory=dict)

    def matches(self, **labels) -> bool:
        return all(self.label.get(k) == v for k, v in labels.items())


class PatchSpecificationMatchFailError(Exception): ...


class Spec(pydantic.BaseModel):
    kind: str
    version: str
    metadata: SpecMetadata
    data: dict[str, Any]
    patch: Optional[list[str]] = None
    ignore_overflowing_patch: bool = True

    def get_classname(self):
        return self.version.split("/")[1]

    def is_patch_fits(self, patches: Optional[Sequence[Patch]] = None):
        if self.patch is None:
            return patches is None

        if patches is None:
            return False

        if len(patches) != len(self.patch):
            return False

        return all(
            given.__class__.__name__ == expected
            for given, expected in zip(patches, self.patch)
        )

    def is_patch_fits_with_overflow(
        self, patches: Optional[Sequence[Patch]] = None
    ) -> tuple[bool, list[Patch]]:
        if self.patch is None:
            return True, []

        if patches is None:
            return False, []

        aligned_patches = []

        my_patch_ptr, given_patch_ptr = 0, 0
        while my_patch_ptr < len(self.patch) and given_patch_ptr < len(patches):
            if patches[given_patch_ptr].__class__.__name__ == self.patch[my_patch_ptr]:
                aligned_patches.append(patches[given_patch_ptr])
                my_patch_ptr += 1
            given_patch_ptr += 1

        return my_patch_ptr == len(self.patch), aligned_patches

    def interpret(self, patches: Optional[Sequence[Patch]] = None):
        if self.ignore_overflowing_patch:
            fits, aligned_patches = self.is_patch_fits_with_overflow(patches)
            if not fits:
                raise PatchSpecificationMatchFailError()
            patches = aligned_patches
        else:
            if not self.is_patch_fits(patches):
                raise PatchSpecificationMatchFailError()

        data = self.data.copy()

        if patches is None:
            return data

        for patch in patches:
            data = patch.apply(data)

        return data
