from typing import Any, Optional, Sequence, Type

from simaple.spec.loadable import get_class
from simaple.spec.patch import Patch
from simaple.spec.repository import SpecRepository
from simaple.spec.spec import Spec


class SpecNotFoundError(Exception):
    ...


class SpecBasedLoader:
    def __init__(self, spec_repository: SpecRepository):
        self._spec_repository = spec_repository

    def load(
        self,
        query: Optional[dict[str, Any]] = None,
        injects: Optional[dict[str, Any]] = None,
        patches: Optional[Sequence[Patch]] = None,
    ) -> Any:
        if query is None:
            query = {}
        if injects is None:
            injects = {}

        specification = self._spec_repository.get(**query)
        if specification is None:
            raise SpecNotFoundError()

        return self.compile_object(specification, injects, patches)

    def load_all(
        self,
        query: Optional[dict[str, Any]] = None,
        injects: Optional[dict[str, Any]] = None,
        patches: Optional[Sequence[Patch]] = None,
    ) -> list[Any]:
        if query is None:
            query = {}
        if injects is None:
            injects = {}

        specifications = self._spec_repository.get_all(**query)

        return [
            self.compile_object(specification, injects, patches)
            for specification in specifications
        ]

    def compile_object(
        self,
        specification: Spec,
        injects: dict[str, Any],
        patches: Optional[Sequence[Patch]],
    ):
        class_name = specification.get_classname()
        component_class = self._get_component_class(class_name, specification.kind)

        try:
            args = {}
            args.update(injects)
            args.update(specification.interpret(patches))
            return component_class(**args)
        except Exception as e:
            raise Exception(
                f"{class_name} <kind: {specification.kind}> parse failed.\nGiven args: {specification}\nError: {e}"
            ) from e

    def _get_component_class(self, clsname: str, kind: str) -> Type[Any]:
        return get_class(clsname, kind=kind)
