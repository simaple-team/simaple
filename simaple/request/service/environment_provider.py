from typing import TypedDict

from loguru import logger

from simaple.container.simulation import FinalCharacterStat
from simaple.core import ExtendedStat, JobType, Stat
from simaple.data.jobs.builtin import get_damage_logic
from simaple.request.service.loader import (
    AbilityLoader,
    CharacterBasicLoader,
    CharacterSkillLoader,
    GearLoader,
    HyperstatLoader,
    LinkSkillLoader,
    PropensityLoader,
    UnionLoader,
)


class EnvironmentProviderServiceResponse(TypedDict):
    final_character_stat: FinalCharacterStat
    level: int
    job_type: JobType
    hexa_skill_levels: dict[str, int]
    hexa_skill_improvements: dict[str, int]


class LoadedEnvironmentProviderService:
    def __init__(
        self,
        ability_loader: AbilityLoader,
        propensity_loader: PropensityLoader,
        hyperstat_loader: HyperstatLoader,
        union_loader: UnionLoader,
        gear_loader: GearLoader,
        character_basic_loader: CharacterBasicLoader,
        link_skill_loader: LinkSkillLoader,
        character_skill_loader: CharacterSkillLoader,
    ):
        self.ability_loader = ability_loader
        self.propensity_loader = propensity_loader
        self.hyperstat_loader = hyperstat_loader
        self.union_loader = union_loader
        self.gear_loader = gear_loader
        self.character_basic_loader = character_basic_loader
        self.link_skill_loader = link_skill_loader
        self.character_skill_loader = character_skill_loader

    def compute_character_info(
        self,
        character_name: str,
    ) -> EnvironmentProviderServiceResponse:
        total_extended_stat = ExtendedStat()
        job_type = self.character_basic_loader.load_character_job_type(character_name)
        character_level = self.character_basic_loader.load_character_level(
            character_name
        )

        temp_damage_logic = get_damage_logic(
            job_type, False
        )  # Force combat orders on; since this is just weak reference

        # Gear Stat
        gear_related_extended_stat = self.gear_loader.load_gear_related_stat(
            character_name
        )
        total_extended_stat += gear_related_extended_stat
        logger.info(
            "Gear Stat: {}",
            gear_related_extended_stat.compute_by_level(character_level).short_dict(),
        )

        # Ability Stat
        ability_extended_stat = self.ability_loader.load_best_stat(
            character_name,
            {"reference_stat": total_extended_stat, "damage_logic": temp_damage_logic},
        )
        total_extended_stat += ability_extended_stat

        # Propensity Stat
        propensity = self.propensity_loader.load_propensity(character_name)
        propensity_extended_stat = propensity.get_extended_stat()
        total_extended_stat += propensity_extended_stat
        logger.info(
            "propensity Stat: {}", propensity.get_extended_stat().stat.short_dict()
        )

        # Hyper Stat
        hyperstat = self.hyperstat_loader.load_hyper_stat(character_name)
        hyperstat_extended_stat = ExtendedStat(stat=hyperstat.get_stat())
        total_extended_stat += hyperstat_extended_stat
        logger.info("Hyper Stat: {}", hyperstat.get_stat().short_dict())

        # Union Stat
        best_union_stat = self.union_loader.load_best_union_stat(
            character_name,
            {"reference_stat": total_extended_stat, "damage_logic": temp_damage_logic},
        )
        total_extended_stat += best_union_stat
        logger.info(
            "Union Squad and Occupation Stat: {}", best_union_stat.stat.short_dict()
        )

        # Union Artifact Stat
        artifacts = self.union_loader.load_union_artifact(character_name)
        artifacts_extended_stat = artifacts.get_extended_stat()
        total_extended_stat += artifacts_extended_stat
        logger.info("Artifact Stat: {}", artifacts_extended_stat.stat.short_dict())

        # Character AP
        character_ap_stat = self.character_basic_loader.load_character_ap_based_stat(
            character_name
        )
        character_ap_extended_stat = ExtendedStat(stat=character_ap_stat)
        total_extended_stat += character_ap_extended_stat
        logger.info("Character AP Stat: {}", character_ap_stat.short_dict())

        logger.info(
            "Intermediate stat {}",
            total_extended_stat.compute_by_level(character_level).short_dict(),
        )

        # Hexa Stat
        hexa_stat = self.character_skill_loader.load_character_hexa_stat(character_name)
        total_extended_stat += ExtendedStat(stat=hexa_stat.get_stat())
        logger.info("Hexa Stat: {}", hexa_stat.get_stat().short_dict())

        (
            zero_grade_skill_stat,
            has_liberated,
        ) = self.character_skill_loader.load_zero_grade_skill_passive_stat(
            character_name
        )
        (
            combat_power_related_stat,
            _,
        ) = self.character_skill_loader.load_combat_power_related_stat(
            character_name,
        )

        damage_logic = get_damage_logic(
            job_type, True
        )  # Force combat orders on; since this is just weak reference

        print(">>", combat_power_related_stat)

        combat_power_basis_stat = (
            (total_extended_stat + combat_power_related_stat).compute_by_level(
                character_level
            )
            + self.gear_loader.get_combat_power_weapon_replacement(character_name)
            + Stat(
                damage_multiplier=(-3.2),
            )
        )
        logger.info("Character level: {}", character_level)
        logger.info(
            "Combar power basis: {}",
            combat_power_basis_stat.short_dict(),
        )
        logger.info(
            "Combat power: {}",
            damage_logic.get_compat_power(
                combat_power_basis_stat, use_genesis_weapon=has_liberated
            ),
        )

        total_extended_stat += zero_grade_skill_stat
        logger.info(
            "Zero grade skill stat: {}", zero_grade_skill_stat.stat.short_dict()
        )

        link_skill_stat = self.link_skill_loader.load_link_skill(character_name)
        logger.info("Link skill stat: {}", link_skill_stat.get_stat().short_dict())

        total_extended_stat += ExtendedStat(stat=link_skill_stat.get_stat())

        character_passive_stat = (
            self.character_skill_loader.load_character_passive_stat(
                character_name, character_level
            )
        )
        total_extended_stat += character_passive_stat

        total_action_stat = total_extended_stat.action_stat
        total_stat = total_extended_stat.compute_by_level(character_level)

        (
            hexa_skill_levels,
            hexa_improvements,
        ) = self.character_skill_loader.load_hexa_skill_levels(character_name)

        logger.info("Final stat: {}", total_stat.short_dict())

        return {
            "final_character_stat": FinalCharacterStat.model_validate(
                {
                    "stat": total_stat,
                    "action_stat": total_action_stat,
                    "active_buffs": {},
                }
            ),
            "level": character_level,
            "job_type": job_type,
            "hexa_skill_levels": hexa_skill_levels,
            "hexa_skill_improvements": hexa_improvements,
        }
