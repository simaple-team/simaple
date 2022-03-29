from __future__ import annotations

from typing import Optional

from simaple.core import DamageLogic, Stat
from simaple.hyperstat import Hyperstat
from simaple.optimizer.optimizer import DiscreteTarget


class HyperstatTarget(DiscreteTarget):
    def __init__(
        self,
        default_stat: Stat,
        damage_logic: DamageLogic,
        hyperstat_prototype: Optional[Hyperstat] = None,
        armor=300,
    ):
        super().__init__(hyperstat_prototype.length())
        self.default_stat = default_stat
        self.damage_logic = damage_logic
        self.armor = armor
        self._hyperstat_prototype = hyperstat_prototype

    def get_hyperstat(self) -> Hyperstat:
        return Hyperstat(
            options=self._hyperstat_prototype.options,
            cost=self._hyperstat_prototype.cost,
            levels=self.state,
        )

    def get_value(self) -> float:
        resulted_stat = self.default_stat + self.get_hyperstat().get_stat()
        return self.damage_logic.get_damage_factor(resulted_stat, armor=self.armor)

    def get_cost(self) -> float:
        return self.get_hyperstat().get_current_cost()

    def clone(self) -> HyperstatTarget:
        target = HyperstatTarget(
            default_stat=self.default_stat,
            damage_logic=self.damage_logic,
            hyperstat_prototype=self._hyperstat_prototype,
        )
        target.set_state(self.state)

        return target

    def get_result(self) -> Hyperstat:
        return self.get_hyperstat()
