from typing import Any, Optional, Type

from simaple.spec.loadable import get_class
from simaple.spec.patch import Patch
from simaple.spec.repository import SpecRepository


class SpecNotFoundError(Exception):
    ...


class SpecBasedLoader:
    def __init__(self, spec_repository: SpecRepository):
        self._spec_repository = spec_repository

    def load(
        self,
        query: Optional[dict[str, Any]] = None,
        injects: Optional[dict[str, Any]] = None,
        patches: Optional[list[Patch]] = None,
    ) -> Any:
        if query is None:
            query = {}
        if injects is None:
            injects = {}

        specification = self._spec_repository.get(**query)
        if specification is None:
            raise SpecNotFoundError()

        class_name = specification.get_classname()
        component_class = self._get_component_class(class_name, specification.kind)

        args = {}
        args.update(injects)
        args.update(specification.interpret(patches))
        return component_class(**args)

    def _get_component_class(self, clsname: str, kind: str) -> Type[Any]:
        return get_class(clsname, kind=kind)
