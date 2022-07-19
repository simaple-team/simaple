from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional

import pydantic

from simaple.fetch.query import Query


class Element(pydantic.BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def run(self, html_text):
        ...


class Promise(pydantic.BaseModel, metaclass=ABCMeta):
    _reserved_promise: Dict[str, Promise] = pydantic.PrivateAttr(default_factory=dict)

    class Config:
        underscore_attrs_are_private = True

    @abstractmethod
    def fetch(self, path, token) -> Dict[str, Any]:
        ...

    def then(self, promises: Dict[str, Promise]):
        self._reserved_promise.update(promises)
        return self

    def resolve(self, path, token) -> Dict:
        result = self.fetch(path, token)

        resolved_result = {}

        for k, v in result.items():
            if isinstance(v, str) and k in self._reserved_promise:
                promise = self._reserved_promise[k]
                resolved_result[k] = promise.resolve(v, token)
            else:
                resolved_result[k] = v

        return resolved_result


class ElementWrapper(Promise):
    element: Element
    query: Query

    reserved_path: Optional[str]

    def fetch(self, path, token) -> Dict[str, Any]:
        if self.reserved_path:
            path = self.reserved_path

        query_result = self.query.get(path, token)
        return self.element.run(query_result)
