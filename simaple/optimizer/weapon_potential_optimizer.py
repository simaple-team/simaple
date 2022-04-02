from __future__ import annotations

from itertools import product
from typing import Iterable, Tuple

from pydantic import BaseModel

from simaple.core import DamageLogic, Stat
from simaple.gear.potential import Potential, PotentialTier

_WEAPON_POTENTIALS = {
    PotentialTier.empty: [
        Stat(attack_power=6),
        Stat(magic_attack=6),
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

    def get_useful_candidates(self, tier):
        PROTECTION_STAT = Stat(ignored_defence=90)
        candidates = [
            stat
            for stat in _WEAPON_POTENTIALS[tier]
            if self.damage_logic.get_damage_factor(
                stat + self.default_stat + PROTECTION_STAT
            )
            - self.damage_logic.get_damage_factor(self.default_stat + PROTECTION_STAT)
            > 0
        ]
        return candidates

    def get_potential_candidates(
        self,
        tiers: Tuple[PotentialTier, PotentialTier, PotentialTier],
        emblem=False,
    ) -> Iterable[Potential]:
        for stats in product(*[self.get_useful_candidates(tier) for tier in tiers]):
            boss_damage_multiplier_count = 0
            ignored_defence_count = 0
            for stat in stats:
                if stat.boss_damage_multiplier > 0:
                    boss_damage_multiplier_count += 1
                if stat.ignored_defence > 0:
                    ignored_defence_count += 1

            if emblem and boss_damage_multiplier_count > 0:
                continue

            if boss_damage_multiplier_count > 2 or ignored_defence_count > 2:
                continue

            yield Potential(options=list(stats))

    def get_reward(self, potential_stat: Stat) -> float:
        stat = self.default_stat + potential_stat
        return self.damage_logic.get_damage_factor(stat, armor=self.armor)

    def get_optimal_potential(self) -> Potential:
        optimal_potential = Potential()
        maximum_reward = 0.0

        for potential in self.get_potential_candidates(self.tiers):
            reward = self.get_reward(potential.get_stat())
            if reward > maximum_reward:
                maximum_reward, optimal_potential = reward, potential

        return optimal_potential

    def get_full_optimal_potential(self) -> Tuple[Potential, Potential, Potential]:
        optimal_potential = (Potential(), Potential(), Potential())
        maximum_reward = 0.0

        iter_count = 0

        weapon_potential_candidates = list(self.get_potential_candidates(self.tiers))
        sub_weapon_potential_candidates = list(
            self.get_potential_candidates(self.tiers)
        )
        emblem_potential_candidates = list(
            self.get_potential_candidates(self.tiers, emblem=True)
        )

        for weapon_potential in weapon_potential_candidates:
            layer1_cached_stat = weapon_potential.get_stat()
            for sub_weapon_potential in sub_weapon_potential_candidates:
                layer2_cached_stat = (
                    layer1_cached_stat + sub_weapon_potential.get_stat()
                )
                for emblem_potential in emblem_potential_candidates:
                    reward = self.get_reward(
                        layer2_cached_stat + emblem_potential.get_stat()
                    )
                    iter_count += 1
                    if reward > maximum_reward:
                        maximum_reward, optimal_potential = reward, (
                            weapon_potential,
                            sub_weapon_potential,
                            emblem_potential,
                        )

        return optimal_potential
