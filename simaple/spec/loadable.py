from __future__ import annotations

import copy
from typing import Any, Type

from pydantic.main import ModelMetaclass


class NamespaceRepository:
    def __init__(self, db_clone=None):
        self._db: dict[str, dict[str, Type[Any]]] = {}
        if db_clone:
            self._db = db_clone

    def add(self, name: str, cls: Type[Any], kind: str) -> None:
        if kind not in self._db:
            self._create_kind(kind)

        self._db[kind][name] = cls

    def get(self, name: str, kind: str) -> Type[Any]:
        return self._db[kind][name]

    def _create_kind(self, kind: str) -> None:
        self._db[kind] = {}

    def copy(self) -> NamespaceRepository:
        return NamespaceRepository(copy.deepcopy(self._db))


_LAYER_NAMESPACE = NamespaceRepository()


def get_all() -> NamespaceRepository:
    return _LAYER_NAMESPACE.copy()


def get_class(name: str, kind: str = "default") -> Type[Any]:
    return _LAYER_NAMESPACE.get(name, kind)


class BaseNamespacedABCMeta(ModelMetaclass, type):
    @classmethod
    def register(mcs, name, cls, kind):
        _LAYER_NAMESPACE.add(name, cls, kind=kind)


def TaggedNamespacedABCMeta(kind="default"):
    """MetaClass generator TaggedNamespacedABCMeta
    Returns Metaclass which kinds given class as `kind` and enable
    access through NamespaceRepository.
    """

    class NamespacedABCMeta(BaseNamespacedABCMeta, type):
        def __new__(mcs, name, bases, namespace, **kwargs):
            cls = super().__new__(mcs, name, bases, namespace, **kwargs)
            mcs.register(name, cls, kind=kind)
            return cls

    return NamespacedABCMeta
