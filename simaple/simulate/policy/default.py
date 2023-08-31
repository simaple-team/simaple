from abc import ABCMeta
from contextlib import contextmanager
from typing import Callable, Generator, Optional

import pydantic

from simaple.simulate.base import Action, Environment, Event
from simaple.simulate.component.view import KeydownView, Running, Validity
from simaple.simulate.policy.base import (
    DSLGeneratorProto,
    OperationGeneratorProto,
    PolicyContextType,
    PolicyWrapper,
    interpret_dsl_generator,
)
from simaple.simulate.reserved_names import Tag


def _get_keydown(environment: Environment) -> Optional[str]:
    keydowns: list[KeydownView] = environment.show("keydown")
    keydown_running_list = [k.name for k in keydowns if k.running]

    return next(iter(keydown_running_list), None)


def get_next_elapse_time(events: list[Event]) -> float:
    for event in events:
        if event.tag in (Tag.DELAY,) and event.payload["time"] > 0:
            return event.payload["time"]  # type: ignore

    return 0.0


def running_map(environment: Environment):
    runnings: list[Running] = environment.show("running")
    running_map = {r.name: r.time_left for r in runnings}
    return running_map


def validity_map(environment: Environment):
    validities: list[Validity] = environment.show("validity")
    validity_map = {v.name: v for v in validities if v.valid}
    return validity_map


def cast_by_priority(order: list[str]) -> DSLGeneratorProto:
    def _gen(ctx: PolicyContextType):
        environment, _ = ctx
        validities = validity_map(environment)
        runnings = running_map(environment)

        for name in order:
            if validities.get(name):
                if runnings.get(name, 0) > 0:
                    continue

                return (yield f"CAST  {name}")

        for v in validities.values():
            if v.valid:
                return (yield f"CAST  {v.name}")

        raise ValueError

    return _gen


def keydown_until_interrupt(
    keydown_skill_name: str, order: list[str]
) -> DSLGeneratorProto:
    def _gen(ctx: PolicyContextType):
        stopby = []
        for name in order:
            if name == keydown_skill_name:
                break
            stopby.append(name)

        while True:
            environment, events = ctx

            validities = validity_map(environment)
            runnings = running_map(environment)

            for name in stopby:
                if validities.get(name):
                    if runnings.get(name, 0) > 0:
                        continue

                    return (yield f"KEYDOWNSTOP  {keydown_skill_name}")

            elapse_time = get_next_elapse_time(events)
            return (yield f"ELAPSE  {elapse_time}")

    return _gen


def default_ordered_policy(order: list[str]) -> OperationGeneratorProto:
    priority_policy = cast_by_priority(order)

    def _gen(ctx: PolicyContextType):
        while True:
            environment, events = ctx

            current_keydown = _get_keydown(environment)
            if current_keydown:
                ctx = yield from keydown_until_interrupt(current_keydown, order)(ctx)
                continue

            elapse_time = get_next_elapse_time(events)
            if elapse_time > 0:
                ctx = yield f"ELAPSE  {elapse_time}"
                continue

            ctx = yield from priority_policy(ctx)

    return _gen


normal_default_ordered_policy = interpret_dsl_generator(default_ordered_policy)
