from abc import ABCMeta
from contextlib import contextmanager
from typing import Optional

import pydantic

from simaple.simulate.base import Action, Environment, Event
from simaple.simulate.component.view import KeydownView, Running, Validity
from simaple.simulate.policy.base import NamedOperation, TimeOperation, KeydownOperation, Operation, get_operand_compiler
from simaple.simulate.reserved_names import Tag
from simaple.simulate.policy.base import DSLBasedPolicy


class DefaultOrderedPolicy(DSLBasedPolicy):
    def __init__(self, order: list[str]) -> None:
        super().__init__()
        self.order = order

    def decide_by_dsl(
        self,
        environment: Environment,
    ) -> str:
        validities: list[Validity] = environment.show("validity")
        runnings: list[Running] = environment.show("running")

        validity_map = {v.name: v for v in validities if v.valid}
        running_map = {r.name: r.time_left for r in runnings}

        target_name = self._decide_target_name(
            validity_map,
            running_map,
        )

        if target_name in self._get_keydown_names(environment):
            stopby = []
            for name in self.order:
                if name == target_name:
                    break
                stopby.append(name)

            return f"KEYDOWN  {target_name}  STOPBY  {'  '.join(stopby)}"

        if target_name:
            return f"CAST  {target_name}"

        raise ValueError(
            "No valid element exist! Maybe unintended component was built?"
        )

    def _decide_target_name(
        self,
        validity_map: dict[str, Validity],
        running_map: dict[str, float],
    ):
        for name in self.order:
            if validity_map.get(name):
                if running_map.get(name, 0) > 0:
                    continue

                return name

        for v in validity_map.values():
            if v.valid:
                return v.name

        return None

    def _get_keydown_names(self, environment: Environment) -> list[str]:
        keydowns: list[KeydownView] = environment.show("keydown")
        return [k.name for k in keydowns]
