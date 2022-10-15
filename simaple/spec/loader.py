import copy
from typing import Generic, TypeVar, Any,Optional
from pydantic.main import ModelMetaclass
from simaple.spec.repository import SpecRepository
from simaple.spec.loadable import get_class


T = TypeVar('T')


class SpecBasedLoader(Generic[T]):
    def __init__(self, spec_repository: SpecRepository):
        self._spec_repository = spec_repository

    def load(self, query: Optional[dict[str, Any]] = None, injects: Optional[dict[str, Any]] = None) -> T:
        if query is None:
            query = {}
        if injects is None:
            injects = {}

        specification = self._spec_repository.get(**query)
        class_name = specification.get_classname()
        component_class = self._get_component_class(class_name, specification.kind)

        args = {}
        args.update(injects)
        args.update(specification.data)
        return component_class(**args)

    def _get_component_class(self, clsname: str, kind: str) -> T:
        return get_class(clsname, kind=kind)
