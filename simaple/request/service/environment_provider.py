from simaple.core import ExtendedStat
from simaple.request.service.loader import (
    AbilityLoader,
    CharacterBasicLoader,
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
    ):
        self.ability_loader = ability_loader
        self.propensity_loader = propensity_loader
        self.hyperstat_loader = hyperstat_loader
        self.union_loader = union_loader
        self.gear_loader = gear_loader
        self.character_basic_loader = character_basic_loader
        self.link_skill_loader = link_skill_loader

    def compute_character(
        self,
        character_name: str,
    ):
        total_extended_stat = ExtendedStat()

        ability_extended_stat = self.ability_loader.load_stat(character_name)
        total_extended_stat += ability_extended_stat

        propensity = self.propensity_loader.load_propensity(character_name)
        propensity_extended_stat = propensity.get_extended_stat()
        total_extended_stat += propensity_extended_stat

        hyperstat = self.hyperstat_loader.load_hyper_stat(character_name)
        hyperstat_extended_stat = ExtendedStat(stat=hyperstat.get_stat())
        total_extended_stat += hyperstat_extended_stat

        union_squad_extended_stat = self.union_loader.load_union_squad_effect(
            character_name
        )
        union_occupation_extended_stat = self.union_loader.load_union_occupation_stat(
            character_name
        )
        total_extended_stat += union_squad_extended_stat
        total_extended_stat += union_occupation_extended_stat

        artifacts = self.union_loader.load_union_artifact(character_name)
        artifacts_extended_stat = artifacts.get_extended_stat()
        total_extended_stat += artifacts_extended_stat

        gear_related_extended_stat = self.gear_loader.load_gear_related_stat(
            character_name
        )
        total_extended_stat += gear_related_extended_stat

        character_ap_stat = self.character_basic_loader.load_character_ap_based_stat(
            character_name
        )
        character_ap_extended_stat = ExtendedStat(stat=character_ap_stat)
        total_extended_stat += character_ap_extended_stat

        link_skill_stat = self.link_skill_loader.load_link_skill(character_name)
        total_extended_stat += ExtendedStat(stat=link_skill_stat.get_stat())

        character_level = self.character_basic_loader.load_character_level(
            character_name
        )

        total_action_stat = total_extended_stat.action_stat
        total_stat = total_extended_stat.compute_by_level(character_level)

        return {
            "character_name": character_name,
            "total_stat": total_stat.model_dump(),
            "total_action_stat": total_action_stat.model_dump(),
        }
