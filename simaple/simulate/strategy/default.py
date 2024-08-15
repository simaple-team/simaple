from typing import Optional

from simaple.simulate.base import Event, ViewerType
from simaple.simulate.component.view import KeydownView, Running, Validity
from simaple.simulate.reserved_names import Tag
from simaple.simulate.strategy.base import RuntimeContextType
from simaple.simulate.strategy.dsl import DSLGeneratorProto, interpret_dsl_generator


def _get_keydown(viewer: ViewerType) -> Optional[str]:
    keydowns: list[KeydownView] = viewer("keydown")
    keydown_running_list = [k.name for k in keydowns if k.running]

    return next(iter(keydown_running_list), None)


def keydown_ended(events: list[Event]) -> bool:
    return any(event["tag"] == Tag.KEYDOWN_END for event in events)


def get_next_elapse_time(events: list[Event]) -> float:
    for event in events:
        if event["tag"] in (Tag.DELAY,) and event["payload"]["time"] > 0:
            return event["payload"]["time"]  # type: ignore

    return 0.0


def running_map(viewer: ViewerType):
    runnings: list[Running] = viewer("running")
    return {r.name: r.time_left for r in runnings}


def validity_map(viewer: ViewerType):
    validities: list[Validity] = viewer("validity")
    return {v.name: v for v in validities if v.valid}


def cast_by_priority(order: list[str]) -> DSLGeneratorProto:
    def _gen(ctx: RuntimeContextType):
        viewer, _ = ctx
        validities = validity_map(viewer)
        runnings = running_map(viewer)

        for name in order:
            if validities.get(name):
                if runnings.get(name, 0) > 0:
                    continue

                return (yield f'CAST "{name}"')

        for v in validities.values():
            if v.valid:
                return (yield f'CAST "{v.name}"')

        raise ValueError

    return _gen


def keydown_until_interrupt(
    keydown_skill_name: str, order: list[str]
) -> DSLGeneratorProto:
    def _gen(ctx: RuntimeContextType):
        stopby = []
        for name in order:
            if name == keydown_skill_name:
                break
            stopby.append(name)

        while True:
            viewer, events = ctx

            validities = validity_map(viewer)
            runnings = running_map(viewer)

            for name in stopby:
                if validities.get(name):
                    if runnings.get(name, 0) > 0:
                        continue

                    return (yield f'KEYDOWNSTOP "{keydown_skill_name}"')

            elapse_time = get_next_elapse_time(events)

            if keydown_ended(events):
                return (yield f'RESOLVE "{keydown_skill_name}"')

            ctx = yield f"ELAPSE {elapse_time}"

    return _gen


def default_ordered_policy(order: list[str]) -> DSLGeneratorProto:
    priority_policy = cast_by_priority(order)

    def _gen(ctx: RuntimeContextType):
        while True:
            viewer, events = ctx

            current_keydown = _get_keydown(viewer)
            if current_keydown:
                ctx = yield from keydown_until_interrupt(current_keydown, order)(ctx)
                continue

            elapse_time = get_next_elapse_time(events)
            if elapse_time > 0:
                ctx = yield f"ELAPSE {elapse_time}"
                continue

            ctx = yield from priority_policy(ctx)

    return _gen


normal_default_ordered_policy = interpret_dsl_generator(default_ordered_policy)
