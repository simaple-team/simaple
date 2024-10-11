

from simaple.simulate.base import Dispatcher, Event, message_signature, Action, Store

from typing import TypedDict, TypeVar, Callable, Any
from functools import wraps


D = TypeVar("D", bound=dict)


def wrap_view_method(view_method: Callable[[D], bool], name: str, binds=None) -> Callable[[D], bool]:
    @wraps(view_method)
    def wrapped(store: Store):
        local_store = store.local(name)

        return view_method(state)

    return wrapped


class FuncionalDispatcher(Dispatcher):
    def __init__(self,
                 name: str,
                 get_default_state: Callable[[], D],
                 reducers: dict[
                     str, Callable[[Any, D], tuple[D, list[Event]]]
                 ],
                 views: dict[str, Callable[[D], bool]
                 ]):
    
        self._name = name
        self._get_default_state = get_default_state
        self._reducers = {
            f"{name}.{k}" : v for k, v in reducers.items()
        }
        self._views = {
            f"{name}.{k}" : v for k, v in views.items()
        }
        self._signatures = list(self._reducers.keys())

    def _includes(self, signature):
        return signature in self._signatures

    def get_default_state(self):
        return self._get_default_state()

    def __call__(self, action: Action, store: Store) -> list[Event]:
        reducer = self._reducers[message_signature(action)]
        return reducer(action, store[self._name])

    def get_views(self):
        return {
            method_name: WrappedView(
                self.name,
                ComponentMethodWrapper(getattr(self, method_name), skip_count=0),
                self.get_default_state(),
                binds=self.binds,
            )
            for method_name in getattr(self, "__views__")
        }
