from functools import wraps
from typing import Any, Callable, TypedDict, TypeVar

from simaple.simulate.core.base import (
    Action,
    Dispatcher,
    Event,
    Store,
    message_signature,
)

D = TypeVar("D", bound=dict)


def wrap_view_method(
    view_method: Callable[[D], bool], name: str, binds=None
) -> Callable[[D], bool]:
    @wraps(view_method)
    def wrapped(store: Store):
        local_store = store.local(name)

        return view_method(state)

    return wrapped
