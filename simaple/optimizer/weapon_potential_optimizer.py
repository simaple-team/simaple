from __future__ import annotations

from itertools import product
from typing import Iterable, Tuple

from pydantic import BaseModel

from simaple.core import DamageLogic, Stat
from simaple.gear.potential import Potential, PotentialTier

_WEAPON_POTENTIALS = {
    PotentialTier.empty: [
        Stat(),
    ],
    PotentialTier.rare: [
        Stat(attack_power_multiplier=3),
        Stat(magic_attack_multiplier=3),
    ],
    PotentialTier.epic: [
        Stat(attack_power_multiplier=6),
        Stat(magic_attack_multiplier=6),
        Stat(ignored_defence=15),
    ],
    PotentialTier.unique: [
        Stat(attack_power_multiplier=9),
        Stat(magic_attack_multiplier=9),
        Stat(ignored_defence=30),
        Stat(boss_damage_multiplier=30),
    ],
    PotentialTier.legendary: [
        Stat(attack_power_multiplier=12),
        Stat(magic_attack_multiplier=12),
        Stat(ignored_defence=40),
        Stat(boss_damage_multiplier=40),
    ],
}


class WeaponPotentialOptimizer(BaseModel):
    default_stat: Stat
    tiers: Tuple[PotentialTier, PotentialTier, PotentialTier]
    damage_logic: DamageLogic
    armor: int = 300

    def get_potential_candidates(
        self, tiers: Tuple[PotentialTier, PotentialTier, PotentialTier]
    ) -> Iterable[Potential]:
        for stats in product(*[_WEAPON_POTENTIALS[tier] for tier in tiers]):
            yield Potential(options=list(stats))

    def get_cost(self, potential: Potential) -> float:
        stat = self.default_stat + potential.get_stat()
        return self.damage_logic.get_damage_factor(stat, armor=self.armor)

    def get_optimal_potential(self) -> Potential:
        optimal_potential = Potential()
        optimal_cost = 0.0

        for potential in self.get_potential_candidates(self.tiers):
            cost = self.get_cost(potential)
            if cost > optimal_cost:
                optimal_cost, optimal_potential = cost, potential

        return optimal_potential
