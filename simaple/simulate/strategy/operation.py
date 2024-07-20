from typing import Callable

from simaple.simulate.base import BehaviorGenerator, Event
from simaple.simulate.policy.base import Operation
from simaple.simulate.reserved_names import Tag
from simaple.simulate.strategy.base import ActionGeneratorType, BehaviorStrategy


def get_next_elapse_time(events: list[Event]) -> float:
    for event in events:
        if event["tag"] in (Tag.DELAY,) and event["payload"]["time"] > 0:
            return event["payload"]["time"]  # type: ignore

    return 0.0


@BehaviorStrategy.operation_handler
def exec_cast(op: Operation, events: list[Event]) -> ActionGeneratorType:
    target_name = op.name

    action = dict(name=target_name, method="use", payload=None)
    events = yield action

    elapse_time = get_next_elapse_time(events)
    if elapse_time == 0:
        return

    yield dict(name="*", method="elapse", payload=elapse_time)


@BehaviorStrategy.operation_handler
def exec_use(op: Operation, events: list[Event]) -> ActionGeneratorType:
    _ = yield dict(name=op.name, method="use", payload=None)


@BehaviorStrategy.operation_handler
def exec_elapse(op: Operation, events: list[Event]) -> ActionGeneratorType:
    _ = yield dict(name="*", method="elapse", payload=op.time)


@BehaviorStrategy.operation_handler
def exec_resolve(op: Operation, events: list[Event]) -> ActionGeneratorType:
    elapse_time = get_next_elapse_time([ev for ev in events if ev["name"] == op.name])
    _ = yield dict(name="*", method="elapse", payload=elapse_time)


@BehaviorStrategy.operation_handler
def exec_keydownstop(op: Operation, events: list[Event]) -> ActionGeneratorType:
    _ = yield dict(name=op.name, method="stop", payload=None)


def get_operations() -> dict[
    str,
    Callable[[Operation], BehaviorGenerator],
]:
    return {
        "CAST": exec_cast,
        "USE": exec_use,
        "ELAPSE": exec_elapse,
        "KEYDOWNSTOP": exec_keydownstop,
        "RESOLVE": exec_resolve,
    }
