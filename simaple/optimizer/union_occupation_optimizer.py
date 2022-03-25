from __future__ import annotations

from typing import Optional

from simaple.core import DamageLogic, Stat
from simaple.optimizer.optimizer import DiscreteTarget
from simaple.union import UnionOccupationStat


class UnionOccupationTarget(DiscreteTarget):
    def __init__(
        self,
        default_stat: Stat,
        damage_logic: DamageLogic,
        armor=300,
        union_occupation_prototype: Optional[UnionOccupationStat] = None,
    ):
        super().__init__(UnionOccupationStat.length(), 40)
        self.default_stat = default_stat
        self.damage_logic = damage_logic
        self.armor = armor
        if union_occupation_prototype is None:
            self._union_occupation_prototype = UnionOccupationStat(
                occupation_state=self.state
            )
        else:
            self._union_occupation_prototype = union_occupation_prototype

    def get_value(self) -> float:
        union_occupation_stat = UnionOccupationStat(
            occupation_state=self.state,
            occupation_value=self._union_occupation_prototype.occupation_value,
        )

        resulted_stat = self.default_stat + union_occupation_stat.get_stat()
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

    def get_result(self) -> UnionOccupationStat:
        return UnionOccupationStat(occupation_state=self.state)
