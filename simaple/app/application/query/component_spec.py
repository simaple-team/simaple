from __future__ import annotations

from simaple.app.domain.uow import UnitOfWork
from simaple.spec.loadable import _LAYER_NAMESPACE


def query_all_component_spec(uow: UnitOfWork) -> dict:
    components = _LAYER_NAMESPACE.get_all(kind="Component")
    return {name: model.schema() for name, model in components.items()}
