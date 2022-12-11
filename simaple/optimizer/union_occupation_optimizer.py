from __future__ import annotations

from simaple.core import DamageLogic, Stat
from simaple.optimizer.optimizer import DiscreteTarget
from simaple.system.union import UnionOccupation


class UnionOccupationTarget(DiscreteTarget):
    def __init__(
        self,
        default_stat: Stat,
        damage_logic: DamageLogic,
        union_occupation_prototype: UnionOccupation,
        armor=300,
    ):
        super().__init__(union_occupation_prototype.length(), 40)
        self.default_stat = default_stat
        self.damage_logic = damage_logic
        self.armor = armor
        self._union_occupation_prototype = union_occupation_prototype

    def _get_union_occupation(self) -> UnionOccupation:
        return self._union_occupation_prototype.get_occupation_rearranged(self.state)

    def get_value(self) -> float:
        resulted_stat = self.default_stat + self._get_union_occupation().get_stat()
        return self.damage_logic.get_damage_factor(resulted_stat, armor=self.armor)

    def get_cost(self) -> float:
        return sum(self.state)

    def clone(self) -> UnionOccupationTarget:
        target = UnionOccupationTarget(
            default_stat=self.default_stat,
            damage_logic=self.damage_logic,
            union_occupation_prototype=self._union_occupation_prototype,
        )
        target.set_state(self.state)

        return target

    def get_result(self) -> UnionOccupation:
        return self._get_union_occupation()
