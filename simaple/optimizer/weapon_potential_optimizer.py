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


# TODO: change into triple-brute-force.
class WeaponPotentialOptimizer(BaseModel):
    default_stat: Stat
    tiers: Tuple[PotentialTier, PotentialTier, PotentialTier]
    damage_logic: DamageLogic
    armor: int = 300
    emblem: bool = False

    def get_potential_candidates(
        self, tiers: Tuple[PotentialTier, PotentialTier, PotentialTier]
    ) -> Iterable[Potential]:
        for stats in product(*[_WEAPON_POTENTIALS[tier] for tier in tiers]):
            boss_damage_multiplier_count = 0
            ignored_defence_count = 0
            for stat in stats:
                if stat.boss_damage_multiplier > 0:
                    boss_damage_multiplier_count += 1
                if stat.ignored_defence > 0:
                    ignored_defence_count += 1

            if self.emblem and boss_damage_multiplier_count > 0:
                continue
            
            if boss_damage_multiplier_count > 3 or ignored_defence_count > 3:
                continue

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
