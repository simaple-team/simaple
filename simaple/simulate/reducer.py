from functools import wraps
from typing import Callable

from simaple.simulate.component.base import WILD_CARD, StaticPayloadReducerInfo
from simaple.simulate.core import Action, message_signature
from simaple.simulate.core.base import Event
from simaple.simulate.core.reducer import ReducerType
from simaple.simulate.core.store import Store


def compute_listening_action(
    owner_name: str, reserved_action_info: str | StaticPayloadReducerInfo
) -> Action:
    if isinstance(reserved_action_info, StaticPayloadReducerInfo):
        return {
            "method": reserved_action_info.name,
            "payload": reserved_action_info.payload,
            "name": owner_name,
        }
    return {"method": reserved_action_info, "name": owner_name, "payload": None}


def wildcard_and_listening_action_reducer(
    owner_name: str, listening_actions: dict[str, str | StaticPayloadReducerInfo]
) -> Callable[[ReducerType], ReducerType]:
    mapped_actions = {
        listener_name: compute_listening_action(owner_name, target)
        for listener_name, target in listening_actions.items()
    }

    anonymous_listeners = {
        listener_name.replace("$", ""): compute_listening_action(owner_name, target)
        for listener_name, target in listening_actions.items()
        if listener_name.startswith("$")
    }

    def wrapper(base_reducer: ReducerType) -> ReducerType:
        @wraps(base_reducer)
        def reducer(action: Action, store: Store) -> list[Event]:
            if action["name"] == WILD_CARD:
                action = {**action, "name": owner_name}
            _action_signature = message_signature(action)

            if anonymous_listeners:
                for (
                    anonymous_listeners_name,
                    anonymous_listeners_action,
                ) in anonymous_listeners.items():
                    if anonymous_listeners_name in _action_signature:
                        print(anonymous_listeners_action, owner_name)
                        anonymous_listeners_action: Action = {
                            **anonymous_listeners_action,
                            "payload": action["payload"],
                        }
                        return base_reducer(anonymous_listeners_action, store)

            if _action_signature in mapped_actions:
                action = mapped_actions[_action_signature]
            return base_reducer(action, store)

        return reducer

    return wrapper


def root_reducer(reducers: list[ReducerType]) -> ReducerType:
    def reducer(action: Action, store: Store) -> list[Event]:
        events = []

        for reducer in reducers:
            events += reducer(action, store)

        return events

    return reducer
