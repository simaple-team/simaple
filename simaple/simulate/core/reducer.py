from typing import Callable, Final, TypedDict

from simaple.simulate.core.action import Action, ActionSignature, get_action_signature
from simaple.simulate.core.base import Event
from simaple.simulate.core.store import Store

ReducerType = Callable[[Action, Store], list[Event]]


def sum_reducers(reducers: list[ReducerType]) -> ReducerType:
    def _reducer(action: Action, store: Store) -> list[Event]:
        events = []

        for reducer in reducers:
            events += reducer(action, store)

        return events

    return _reducer


_ANONYMOUS_REDUCER_SIGNATURE: Final[ActionSignature] = (
    "__anonymous__",
    "__annonymous__",
)


class ReducerPrecursor(TypedDict):
    """
    If the target_action_signature is empty, then this is dynamic-target reducer;
    """

    unsafe_reducer: ReducerType
    name: ActionSignature
    target_action_signature: list[ActionSignature]


def is_dynamic_target_reducer_precursor(reducer_precursor: ReducerPrecursor) -> bool:
    return len(reducer_precursor["target_action_signature"]) == 0


class Listener(TypedDict):
    action_name_or_reserved_values: str
    action_method: str

    target_reducer_name: ActionSignature
    payload: dict | None


def _as_static_payload_reducer(
    name: str, method: str, payload: dict | None, reducer: ReducerType
):

    def static_payload_reducer(action: Action, store: Store) -> list[Event]:
        updated_action: Action = {"name": name, "method": method, "payload": payload}
        if payload is None:
            updated_action["payload"] = action["payload"]

        return reducer(updated_action, store)

    return static_payload_reducer


def identity_reducer(reducer: ReducerType) -> ReducerType:
    def identity(action: Action, store: Store) -> list[Event]:
        print(action)
        return reducer(action, store)

    return identity


def anonymous_reducer(reducer: ReducerType, method_postfix: str) -> ReducerType:
    def _reducer(action: Action, store: Store) -> list[Event]:
        if not action["method"].endswith(method_postfix):
            return []
        print("!", action)
        return reducer(action, store)

    return _reducer


def listener_to_reducer_precursor(
    listener: Listener,
    reducer_precursors: list[ReducerPrecursor],
) -> ReducerPrecursor:
    target_reducer_precursor = None
    for reducer_precursor in reducer_precursors:
        if listener["target_reducer_name"] == reducer_precursor["name"]:
            target_reducer_precursor = reducer_precursor

    if target_reducer_precursor is None:
        raise ValueError("Target reducer not found")

    reducer = _as_static_payload_reducer(
        listener["target_reducer_name"][0],
        listener["target_reducer_name"][1],
        listener["payload"],
        target_reducer_precursor["unsafe_reducer"],
    )

    if listener["action_name_or_reserved_values"] == "$":
        return {
            "unsafe_reducer": anonymous_reducer(reducer, listener["action_method"]),
            "name": _ANONYMOUS_REDUCER_SIGNATURE,
            "target_action_signature": [],
        }  # dynamic-target reducer

    target_action = (
        listener["action_name_or_reserved_values"],
        listener["action_method"],
    )

    return {
        "unsafe_reducer": reducer,
        "name": _ANONYMOUS_REDUCER_SIGNATURE,
        "target_action_signature": [target_action],
    }


def create_safe_reducer(
    reducer_precursors: list[ReducerPrecursor],
):
    full_action_signature_set = sum(
        (precursor["target_action_signature"] for precursor in reducer_precursors), []
    )

    action_signature_to_unsafe_reducers = {
        action_signature: [
            precursor["unsafe_reducer"]
            for precursor in reducer_precursors
            if action_signature in precursor["target_action_signature"]
        ]
        for action_signature in full_action_signature_set
    }

    dynamic_target_reducers = [
        precursor["unsafe_reducer"]
        for precursor in reducer_precursors
        if is_dynamic_target_reducer_precursor(precursor)
    ]

    for k, v in action_signature_to_unsafe_reducers.items():
        print(k, ">>", len(v), v)

    def root_reducer(action: Action, store: Store) -> list[Event]:
        action_signature = get_action_signature(action)
        events = []

        if action_signature not in action_signature_to_unsafe_reducers:
            # print("No reducer for", action_signature)
            for unsafe_reducer in dynamic_target_reducers:
                events.extend(unsafe_reducer(action, store))

            return []

        unsafe_reducers = action_signature_to_unsafe_reducers[action_signature]

        for unsafe_reducer in unsafe_reducers + dynamic_target_reducers:
            events.extend(unsafe_reducer(action, store))

        return events

    return root_reducer
