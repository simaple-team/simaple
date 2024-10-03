from loguru import logger

from simaple.core import ExtendedStat
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


class LoadedEnvironmentProvider:
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

    def compute_character(
        self,
        character_name: str,
    ):
        total_extended_stat = ExtendedStat()
        job_type = self.character_basic_loader.load_character_job_type(character_name)
        character_level = self.character_basic_loader.load_character_level(
            character_name
        )

        damage_logic = get_damage_logic(
            job_type, True
        )  # Force combat orders on; since this is just weak reference

        gear_related_extended_stat = self.gear_loader.load_gear_related_stat(
            character_name
        )
        total_extended_stat += gear_related_extended_stat
        logger.info(
            "Gear Stat: {}",
            gear_related_extended_stat.compute_by_level(character_level).short_dict(),
        )

        ability_extended_stat = self.ability_loader.load_best_stat(
            character_name,
            {"reference_stat": total_extended_stat, "damage_logic": damage_logic},
        )
        total_extended_stat += ability_extended_stat

        propensity = self.propensity_loader.load_propensity(character_name)
        propensity_extended_stat = propensity.get_extended_stat()
        total_extended_stat += propensity_extended_stat
        logger.info(
            "propensity Stat: {}", propensity.get_extended_stat().stat.short_dict()
        )

        hyperstat = self.hyperstat_loader.load_hyper_stat(character_name)
        hyperstat_extended_stat = ExtendedStat(stat=hyperstat.get_stat())
        total_extended_stat += hyperstat_extended_stat
        logger.info("Hyper Stat: {}", hyperstat.get_stat().short_dict())

        union_squad_extended_stat = self.union_loader.load_union_squad_effect(
            character_name
        )
        union_occupation_extended_stat = self.union_loader.load_union_occupation_stat(
            character_name
        )
        total_extended_stat += union_squad_extended_stat
        total_extended_stat += union_occupation_extended_stat
        logger.info("Union Squad Stat: {}", union_squad_extended_stat.stat.short_dict())
        logger.info(
            "Union Occupation Stat: {}",
            union_occupation_extended_stat.stat.short_dict(),
        )

        artifacts = self.union_loader.load_union_artifact(character_name)
        artifacts_extended_stat = artifacts.get_extended_stat()
        total_extended_stat += artifacts_extended_stat
        logger.info("Artifact Stat: {}", artifacts_extended_stat.stat.short_dict())

        character_ap_stat = self.character_basic_loader.load_character_ap_based_stat(
            character_name
        )
        character_ap_extended_stat = ExtendedStat(stat=character_ap_stat)
        total_extended_stat += character_ap_extended_stat

        logger.info(
            "Intermediate stat(10) {}",
            total_extended_stat.compute_by_level(character_level).short_dict(),
        )

        hexa_stat = self.character_skill_loader.load_character_hexa_stat(character_name)
        total_extended_stat += ExtendedStat(stat=hexa_stat.get_stat())
        logger.info("Hexa Stat: {}", hexa_stat.get_stat().short_dict())

        logger.info("Character level: {}", character_level)
        logger.info(
            "Stat before adding skills: {}",
            total_extended_stat.compute_by_level(character_level).short_dict(),
        )

        print(
            "Combat power",
            damage_logic.get_compat_power(
                total_extended_stat.compute_by_level(character_level)
            ),
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

        return {
            "character_name": character_name,
            "total_stat": total_stat.model_dump(),
            "total_action_stat": total_action_stat.model_dump(),
        }
