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
from simaple.job.job import Job
from simaple.link import LinkSkillset
from simaple.optimizer import (
    HyperstatTarget,
    LinkSkillTarget,
    StepwizeOptimizer,
    UnionOccupationTarget,
    UnionSquadTarget,
    WeaponPotentialOptimizer,
)
from simaple.union import UnionOccupation, UnionSquad
from simaple.util import Timer


class Preset(BaseModel):
    gearset: Gearset
    hyperstat: Hyperstat
    links: LinkSkillset

    union_squad: UnionSquad
    union_occupation: UnionOccupation

    # inner_ability: InnerAbility

    level: int
    level_stat: Stat

    def get_total_stat(self) -> Stat:
        return (
            self.gearset.get_total_stat()
            + self.hyperstat.get_stat()
            + self.links.get_stat()
            + self.union_squad.get_stat()
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
    weapon_potential_tier: Tuple[PotentialTier, PotentialTier, PotentialTier]

    @classmethod
    def based_on_job(
        cls,
        job: Job,
        union_block_count: int,
        alternate_character_job_types: List[JobType],
        link_count: int,
        weapon_potential_tier: Tuple[PotentialTier, PotentialTier, PotentialTier],
    ):
        return PresetOptimizer(
            default_stat=job.get_default_stat(),
            level=job.level,
            level_stat=job.level_stat,
            damage_logic=job.damage_logic,
            character_job_type=job.type,
            union_block_count=union_block_count,
            alternate_character_job_types=alternate_character_job_types,
            link_count=link_count,
            weapon_potential_tier=weapon_potential_tier,
        )

    def calculate_optimal_hyperstat(self, reference_stat: Stat) -> Hyperstat:
        with Timer("hyperstat"):
            hyperstat_optimization_target = HyperstatTarget(
                reference_stat,
                self.damage_logic,
                Hyperstat(),
            )
            optimizer = StepwizeOptimizer(
                hyperstat_optimization_target,
                Hyperstat.get_maximum_cost_from_level(self.level),
                1,
            )
            output = optimizer.optimize()

        result: Hyperstat = output.get_result()
        return result

    def calculate_optimal_union_squad(self, reference_stat: Stat) -> UnionSquad:
        with Timer("union_squad"):
            union_squad_optimization_target = UnionSquadTarget(
                reference_stat,
                self.damage_logic,
                UnionSquad.create_with_some_large_blocks(
                    large_block_jobs=[self.character_job_type]
                    + self.alternate_character_job_types,
                ),
                preempted_jobs=[self.character_job_type]
                + self.alternate_character_job_types,
            )
            optimizer = StepwizeOptimizer(
                union_squad_optimization_target, self.union_block_count, 2
            )
            output = optimizer.optimize()

        result: UnionSquad = output.get_result()
        return result

    def calculate_optimal_union_occupation(
        self, reference_stat: Stat, occupation_count: int
    ) -> UnionOccupation:
        with Timer("union_occupation"):
            union_occupation_target = UnionOccupationTarget(
                reference_stat,
                self.damage_logic,
                UnionOccupation(),
            )
            optimizer = StepwizeOptimizer(union_occupation_target, occupation_count, 2)
            output = optimizer.optimize()

        result: UnionOccupation = output.get_result()
        return result

    def calculate_optimal_links(self, reference_stat: Stat) -> LinkSkillset:
        with Timer("links"):
            optimization_target = LinkSkillTarget(
                reference_stat,
                self.damage_logic,
                LinkSkillset.KMS(),
                preempted_jobs=[self.character_job_type],
            )
            optimizer = StepwizeOptimizer(optimization_target, self.link_count, 1)
            output = optimizer.optimize()

        result: LinkSkillset = output.get_result()
        return result

    def calculate_optimal_weapon_potential(
        self, reference_stat: Stat
    ) -> Tuple[Potential, Potential, Potential]:
        with Timer("weapon potential"):
            potentials = WeaponPotentialOptimizer(
                default_stat=reference_stat,
                tiers=self.weapon_potential_tier,
                damage_logic=self.damage_logic,
            ).get_full_optimal_potential()

        return potentials

    def create_optimal_preset_from_gearset(self, gearset_prototype: Gearset) -> Preset:
        gearset = gearset_prototype.copy()

        preset = Preset(
            gearset=gearset,
            hyperstat=Hyperstat(),
            links=LinkSkillset.empty(),
            union_squad=UnionSquad.empty(),
            union_occupation=UnionOccupation(),
            level=self.level,
            level_stat=self.level_stat,
        )

        for i in range(2):
            self._optimize_step(preset)

        return preset

    def _optimize_step(self, preset):
        # Cleanse gearset weapon potentials for further optimization.
        for slot in preset.gearset.get_weaponry_slots():
            slot.get_gear().potential = Potential()

        preset.gearset.change_weaponry_potentials(
            self.calculate_optimal_weapon_potential(
                preset.get_total_stat() + self.default_stat
            )
        )

        preset.links = LinkSkillset.empty()
        preset.links = self.calculate_optimal_links(
            preset.get_total_stat() + self.default_stat
        )

        preset.union_squad = UnionSquad.empty()
        preset.union_squad = self.calculate_optimal_union_squad(
            preset.get_total_stat() + self.default_stat
        )

        preset.hyperstat = Hyperstat()
        preset.hyperstat = self.calculate_optimal_hyperstat(
            preset.get_total_stat() + self.default_stat
        )

        preset.union_occupation = UnionOccupation()
        preset.union_occupation = self.calculate_optimal_union_occupation(
            preset.get_total_stat() + self.default_stat,
            preset.union_squad.get_occupation_count(),
        )
