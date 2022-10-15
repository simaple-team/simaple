from __future__ import annotations

import copy
from typing import Generic
from pydantic.main import ModelMetaclass


class NamespaceRepository:
    def __init__(self):
        self._db = {}

    def add(self, name, cls, kind):
        if kind not in self._db:
            self._create_kind(kind)

        self._db[kind][name] = cls

    def get(self, name, kind):
        return self._db[kind][name]

    def _create_kind(self, kind):
        self._db[kind] = {}

    def copy(self) -> NamespaceRepository:
        return NamespaceRepository(copy.deepcopy(self._db))


_LAYER_NAMESPACE = NamespaceRepository()


def get_all() -> NamespaceRepository:
    return _LAYER_NAMESPACE.copy()


def get_class(name: str, kind: str = "default"):
    return _LAYER_NAMESPACE.get(name, kind)


def TaggedNamespacedABCMeta(kind="default"):
    """MetaClass generator TaggedNamespacedABCMeta
    Returns Metaclass which kinds given class as `kind` and enable
    access through NamespaceRepository.
    """

    class NamespacedABCMeta(ModelMetaclass, type):
        def __new__(mcs, name, bases, namespace, **kwargs):
            cls = super().__new__(mcs, name, bases, namespace, **kwargs)
            _LAYER_NAMESPACE.add(name, cls, kind=kind)
            return cls

    return NamespacedABCMeta
