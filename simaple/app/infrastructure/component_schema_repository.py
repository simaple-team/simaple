from typing import Optional, Type

from pydantic.main import BaseModel

from simaple.app.domain.component_schema import (
    ComponentSchema,
    ComponentSchemaRepository,
)
from simaple.spec.loadable import get_all, get_class


class LoadableComponentSchemaRepository(ComponentSchemaRepository):
    def get(self, name: str) -> Optional[ComponentSchema]:
        return self._component_cls_to_schema(name, get_class(name, "Component"))

    def get_all(self) -> list[ComponentSchema]:
        component_cls_map = get_all("Component")
        return [
            self._component_cls_to_schema(name, model)
            for name, model in component_cls_map.items()
        ]

    def _component_cls_to_schema(self, name, model: Type[BaseModel]) -> ComponentSchema:
        return ComponentSchema(
            name=name,
            value=model.schema(),
        )
