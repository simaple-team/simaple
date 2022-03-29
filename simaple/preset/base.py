"""
preset.py

Job independant description about character.
Give gearset / hyperstat / link / union / inner-ability attached property.
"""
from typing import List, Tuple

from pydantic import BaseModel

from simaple.core import DamageLogic, JobType, Stat
from simaple.gear.gearset import Gearset
from simaple.gear.potential import Potential, PotentialTier
from simaple.hyperstat import Hyperstat
from simaple.link import LinkSkillset
from simaple.optimizer import (
    HyperstatTarget,
    LinkSkillTarget,
    StepwizeOptimizer,
    UnionBlockTarget,
    UnionOccupationTarget,
    WeaponPotentialOptimizer,
)
from simaple.union import UnionBlockstat, UnionOccupationStat
from simaple.util import Timer


class Preset(BaseModel):
    gearset: Gearset
    hyperstat: Hyperstat
    links: LinkSkillset

    union_blocks: UnionBlockstat
    union_occupation: UnionOccupationStat

    # inner_ability: InnerAbility

    level: int
    level_stat: Stat

    def get_total_stat(self) -> Stat:
        return (
            self.gearset.get_total_stat()
            + self.hyperstat.get_stat()
            + self.links.get_stat()
            + self.union_blocks.get_stat()
            + self.union_occupation.get_stat()
            + self.level_stat
        )


class PresetOptimizer(BaseModel):
    union_block_count: int
    default_stat: Stat
    level: int
    level_stat: Stat
    damage_logic: DamageLogic
    character_job_type: JobType
    alternate_character_job_types: List[JobType]
    link_count: int
    weapon_potential_tiers: List[Tuple[PotentialTier, PotentialTier, PotentialTier]]

    def calculate_optimal_hyperstat(self, reference_stat: Stat) -> Hyperstat:
        with Timer("hyperstat"):
            hyperstat_optimization_target = HyperstatTarget(
                reference_stat,
                self.damage_logic,
            )
            optimizer = StepwizeOptimizer(
                hyperstat_optimization_target,
                Hyperstat.get_maximum_cost_from_level(self.level),
                1,
            )
            output = optimizer.optimize()

        return output.get_result()

    def calculate_optimal_union_blocks(self, reference_stat: Stat) -> UnionBlockstat:
        with Timer("union_blocks"):
            union_block_optimization_target = UnionBlockTarget(
                reference_stat,
                self.damage_logic,
                preempted_jobs=[self.character_job_type]
                + self.alternate_character_job_types,
            )
            optimizer = StepwizeOptimizer(
                union_block_optimization_target, self.union_block_count, 2
            )
            output = optimizer.optimize()

        return output.get_result()

    def calculate_optimal_union_occupation(
        self, reference_stat: Stat, occupation_count: int
    ) -> UnionOccupationStat:
        with Timer("union_occupation"):
            union_occupation_target = UnionOccupationTarget(
                reference_stat,
                self.damage_logic,
            )
            optimizer = StepwizeOptimizer(union_occupation_target, occupation_count, 2)
            output = optimizer.optimize()

        return output.get_result()

    def calculate_optimal_links(self, reference_stat: Stat) -> LinkSkillset:
        with Timer("links"):
            optimization_target = LinkSkillTarget(
                reference_stat,
                self.damage_logic,
                preempted_jobs=[self.character_job_type],
            )
            optimizer = StepwizeOptimizer(optimization_target, self.link_count, 1)
            output = optimizer.optimize()

        return output.get_result()

    def calculate_optimal_weapon_potential(
        self, reference_stat: Stat
    ) -> List[Potential]:
        with Timer("weapon potential"):
            potentials: List[Potential] = []

            for tiers in self.weapon_potential_tiers:
                potential = WeaponPotentialOptimizer(
                    default_stat=reference_stat
                    + sum([potential.get_stat() for potential in potentials], Stat()),
                    tiers=tiers,
                    damage_logic=self.damage_logic,
                )
                potentials.append(potential.get_optimal_potential())

        return potentials

    def get_static_reference_stat(self, gearset: Gearset) -> Stat:
        return gearset.get_total_stat() + self.level_stat + self.default_stat

    def create_optimal_preset_from_gearset(self, gearset_prototype: Gearset) -> Preset:
        gearset = gearset_prototype.copy()

        # Cleanse gearset weapon potentials
        for slot_name in ("weapon", "subweapon", "emblem"):
            target_gear = gearset.get_slot(slot_name).gear
            if target_gear is None:
                raise ValueError(f"item not set for {slot_name}")
            target_gear.potential = Potential()

        reference_stat = self.get_static_reference_stat(gearset)

        links = self.calculate_optimal_links(reference_stat)
        union_blocks = self.calculate_optimal_union_blocks(reference_stat)

        intermediate_stat = reference_stat + links.get_stat() + union_blocks.get_stat()

        # Iteratively - optimization

        hyperstat = self.calculate_optimal_hyperstat(intermediate_stat)
        hyperstat_stat = hyperstat.get_stat()

        union_occupation_count = union_blocks.get_occupation_count()
        union_occupation = self.calculate_optimal_union_occupation(
            intermediate_stat + hyperstat_stat, union_occupation_count
        )
        union_occupation_stat = union_occupation.get_stat()

        optimal_potentials = self.calculate_optimal_weapon_potential(
            intermediate_stat + hyperstat_stat + union_occupation_stat
        )
        optimal_potential_stat = sum(
            [potential.get_stat() for potential in optimal_potentials], Stat()
        )

        # Apply potential to gearset
        for idx, slot_name in enumerate(("weapon", "subweapon", "emblem")):
            target_gear = gearset.get_slot(slot_name).gear
            if target_gear is None:
                raise ValueError(f"item not set for {slot_name}")

            target_gear.potential = optimal_potentials[idx]

        return Preset(
            gearset=gearset,
            hyperstat=hyperstat,
            links=links,
            union_blocks=union_blocks,
            union_occupation=union_occupation,
            level=self.level,
            level_stat=self.level_stat,
        )
