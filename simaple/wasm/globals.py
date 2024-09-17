import abc

from simaple.data.jobs.builtin import get_kms_spec_resource_path
from simaple.spec.repository import DirectorySpecRepository, SpecRepository


class InternalDatabase:
    def __init__(self, spec_repository: SpecRepository):
        self._spec_repository = spec_repository

    def spec_repository(self) -> SpecRepository:
        return self._spec_repository


_GLOBAL_INTERNAL_DATABASE: InternalDatabase | None = None


def get_internal_database() -> InternalDatabase:
    global _GLOBAL_INTERNAL_DATABASE
    if _GLOBAL_INTERNAL_DATABASE is None:
        _GLOBAL_INTERNAL_DATABASE = InternalDatabase(
            DirectorySpecRepository(get_kms_spec_resource_path())
        )

    return _GLOBAL_INTERNAL_DATABASE
