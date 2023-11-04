from typing import Callable

from simaple.simulate.base import Event
from simaple.simulate.policy.base import (
    ActionGeneratorType,
    BehaviorGenerator,
    Operation,
    _BehaviorGenerator,
)
from simaple.simulate.reserved_names import Tag


def get_next_elapse_time(events: list[Event]) -> float:
    for event in events:
        if event["tag"] in (Tag.DELAY,) and event["payload"]["time"] > 0:
            return event["payload"]["time"]  # type: ignore

    return 0.0


@BehaviorGenerator.operation_handler
def exec_cast(op: Operation, events: list[Event]) -> ActionGeneratorType:
    target_name = op.name

    action = dict(name=target_name, method="use")
    events = yield action

    elapse_time = get_next_elapse_time(events)
    if elapse_time == 0:
        return

    yield dict(name="*", method="elapse", payload=elapse_time)


@BehaviorGenerator.operation_handler
def exec_use(op: Operation, events: list[Event]) -> ActionGeneratorType:
    _ = yield dict(name=op.name, method="use", payload=None)


@BehaviorGenerator.operation_handler
def exec_elapse(op: Operation, events: list[Event]) -> ActionGeneratorType:
    _ = yield dict(name="*", method="elapse", payload=op.time)


@BehaviorGenerator.operation_handler
def exec_resolve(op: Operation, events: list[Event]) -> ActionGeneratorType:
    elapse_time = get_next_elapse_time([ev for ev in events if ev["name"] == op.name])
    _ = yield dict(name="*", method="elapse", payload=elapse_time)


@BehaviorGenerator.operation_handler
def exec_keydownstop(op: Operation, events: list[Event]) -> ActionGeneratorType:
    _ = yield dict(name=op.name, method="stop", payload=None)


def get_operations() -> dict[
    str,
    Callable[[Operation], _BehaviorGenerator],
]:
    return {
        "CAST": exec_cast,
        "USE": exec_use,
        "ELAPSE": exec_elapse,
        "KEYDOWNSTOP": exec_keydownstop,
        "RESOLVE": exec_resolve,
    }
