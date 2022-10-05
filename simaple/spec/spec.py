from typing import Any, Optional

import pydantic


class SpecMetadata(pydantic.BaseModel):
    label: Optional[dict[str, Any]]
    annotation: Optional[dict[str, Any]]

    def matches(self, **labels) -> bool:
        return all(self.label.get(k) == v for k, v in labels.items())


class PatchSpecificationMatchFailError(Exception):
    ...


class Spec(pydantic.BaseModel):
    kind: str
    version: str
    metadata: SpecMetadata
    data: dict[str, Any]
    patch: Optional[list[str]]

    def is_patch_fits(self, patches: Optional[list] = None):
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

    def interpret(self, patches: Optional[list] = None):
        if not self.is_patch_fits(patches):
            raise PatchSpecificationMatchFailError()

        data = self.data.copy()
        for patch in patches:
            data = patch.apply(data)

        return data
