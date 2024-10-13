from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Optional, cast

from pydantic import BaseModel, ConfigDict

from simaple.simulate.core.base import Action, Entity, Event
from simaple.spec.loadable import get_class  # pylint:disable=unused-import


class Store(metaclass=ABCMeta):
    def use_entity(self, name: str, default: Entity):
        def entity_setter(state):
            self.set_entity(name, state)

        return self.read_entity(name, default=default), entity_setter

    @abstractmethod
    def read(self, name: str) -> dict[str, Entity]: ...

    @abstractmethod
    def read_entity(self, name: str, default: Entity | None): ...

    @abstractmethod
    def set_entity(self, name: str, entity: Entity): ...

    @abstractmethod
    def local(self, address: str) -> Store: ...

    @abstractmethod
    def save(self) -> Any: ...

    @abstractmethod
    def load(self, saved_store) -> None: ...


class ConcreteStore(Store):
    def __init__(self) -> None:
        self._entities: dict[str, Entity] = {}
        self._owned_entities: dict[str, list[str]] = defaultdict(list)

    def set_entity(self, name: str, entity: Entity) -> None:
        self._entities[name] = entity

        if len(name.split(".")) == 3:
            _, owner, entity_name = name.split(".")
            self._owned_entities[owner].append(entity_name)

    def read(self, owner: str) -> dict[str, Entity]:
        return {
            entity_name: self.read_entity(f".{owner}.{entity_name}", None)
            for entity_name in self._owned_entities[owner]
        }

    def read_entity(self, name: str, default: Optional[Entity]):
        if default is None:
            value = self._entities.get(name)
        else:
            value = self._entities.setdefault(name, default)
        if value is None:
            raise ValueError(
                f"No entity exists: {name}. None-default only enabled for external-property binding. Maybe missing global proeperty installation?"
            )
        return value

    def local(self, address):
        return self

    def save(self) -> Any:
        return {k: self._save_entity(v) for k, v in self._entities.items()}

    def load(self, saved_store: dict[str, dict]) -> None:
        for k, v in saved_store.items():
            self.set_entity(k, self._load_entity(v))

    def _save_entity(self, entity: Entity) -> dict:
        entity_clsname = entity.__class__.__name__
        return {
            "cls": entity_clsname,
            "payload": entity.model_dump(),
        }

    def _load_entity(self, saved_entity_dict: dict) -> Entity:
        clsname, payload = saved_entity_dict["cls"], saved_entity_dict["payload"]
        return cast(Entity, get_class(clsname, kind="Entity").model_validate(payload))


class AddressedStore(Store):
    def __init__(self, concrete_store: ConcreteStore, current_address: str = ""):
        self._current_address = current_address
        self._concrete_store = concrete_store

    def read(self, owner: str) -> dict[str, Entity]:
        return self._concrete_store.read(owner)

    def set_entity(self, name: str, entity: Entity):
        address = self._resolve_address(name)
        return self._concrete_store.set_entity(address, entity)

    def read_entity(self, name: str, default: Optional[Entity]):
        address = self._resolve_address(name)
        return self._concrete_store.read_entity(address, default)

    def local(self, address: str):
        return AddressedStore(
            self._concrete_store, f"{self._current_address}.{address}"
        )

    def _resolve_address(self, name: str):
        """descriminate local-variable (no period) and global-variable (with period)"""
        if len(name.split(".")) == 1:
            return f"{self._current_address}.{name}"

        return name

    def save(self):
        return self._concrete_store.save()

    def load(self, saved_store):
        return self._concrete_store.load(saved_store)


class Checkpoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    store_ckpt: dict[str, Any]

    @classmethod
    def create(
        cls,
        store: AddressedStore,
    ) -> Checkpoint:
        return Checkpoint(store_ckpt=store.save())

    def restore(self) -> AddressedStore:
        concrete_store = ConcreteStore()
        concrete_store.load(self.store_ckpt)
        store = AddressedStore(concrete_store)
        return store
