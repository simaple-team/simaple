from __future__ import annotations

from simaple.core import DamageLogic, Stat
from simaple.optimizer.optimizer import DiscreteTarget
from simaple.system.hyperstat import Hyperstat


class HyperstatTarget(DiscreteTarget):
    def __init__(
        self,
        default_stat: Stat,
        damage_logic: DamageLogic,
        hyperstat_prototype: Hyperstat,
        armor=300,
    ):
        super().__init__(hyperstat_prototype.length())
        self.default_stat = default_stat
        self.damage_logic = damage_logic
        self.armor = armor
        self._hyperstat_prototype = hyperstat_prototype

    def _get_hyperstat(self) -> Hyperstat:
        return self._hyperstat_prototype.get_level_rearranged(self.state)

    def get_value(self) -> float:
        resulted_stat = self.default_stat + self._get_hyperstat().get_stat()
        return self.damage_logic.get_damage_factor(resulted_stat, armor=self.armor)

    def get_cost(self) -> float:
        return self._get_hyperstat().get_current_cost()

    def clone(self) -> HyperstatTarget:
        target = HyperstatTarget(
            default_stat=self.default_stat,
            damage_logic=self.damage_logic,
            hyperstat_prototype=self._hyperstat_prototype,
        )
        target.set_state(self.state)

        return target

    def get_result(self) -> Hyperstat:
        return self._get_hyperstat()
