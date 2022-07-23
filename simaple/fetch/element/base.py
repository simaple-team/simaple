from __future__ import annotations

import asyncio
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
    async def fetch(self, path, token) -> Dict[str, Any]:
        ...

    def then(self, promises: Dict[str, Promise]):
        self._reserved_promise.update(promises)
        return self

    async def resolve(self, path, token) -> Dict:
        result = await self.fetch(path, token)

        resolved_result = {}

        reserved_promise = []
        reserved_promise_key = []

        for k, v in result.items():
            if isinstance(v, str) and k in self._reserved_promise:
                reserved_promise.append(
                    asyncio.ensure_future(self._reserved_promise[k].resolve(v, token))
                )
                reserved_promise_key.append(k)
                # promise = self._reserved_promise[k]
                # resolved_result[k] = await promise.resolve(v, token)
            else:
                resolved_result[k] = v

        resolved_promise_results = await asyncio.gather(*reserved_promise)
        for k, v in zip(reserved_promise_key, resolved_promise_results):
            resolved_result[k] = v

        return resolved_result


class ElementWrapper(Promise):
    element: Element
    query: Query

    reserved_path: Optional[str]

    async def fetch(self, path, token) -> Dict[str, Any]:
        if self.reserved_path:
            path = self.reserved_path

        query_result = await self.query.get(path, token)
        return self.element.run(query_result)
