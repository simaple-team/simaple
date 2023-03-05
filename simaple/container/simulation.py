import json
import os
from typing import Callable

import pydantic
from dependency_injector import containers, providers

from simaple.core import ActionStat, ExtendedStat, JobCategory, JobType, Stat
from simaple.data.ability import get_best_ability
from simaple.data.baseline import get_baseline_gearset
from simaple.data.client_configuration import get_client_configuration
from simaple.data.damage_logic import get_damage_logic
from simaple.data.doping import get_normal_doping
from simaple.data.monster_life import get_normal_monsterlife
from simaple.data.passive import get_passive
from simaple.gear.gearset import Gearset
from simaple.optimizer.preset import Preset, PresetOptimizer
from simaple.simulate.kms import get_client
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage
from simaple.system.ability import get_ability_stat
from simaple.system.trait import CharacterTrait


class SimulationSetting(pydantic.BaseSettings):
    tier: str
    jobtype: JobType
    job_category: JobCategory
    level: int

    use_doping: bool = True
    passive_skill_level: int
    combat_orders_level: int
    union_block_count: int = 37
    link_count: int = 12 + 1
    armor: int = 300
    mob_level: int = 265
    force_advantage: float = 1.0
    trait_level: int = 100

    v_skill_level: int = 30
    v_improvements_level: int = 60

    weapon_attack_power: int = 0
    weapon_pure_attack_power: int = 0

    cache_root_dir: str = ""

    def get_preset_hash(self) -> str:
        preset_hash = (
            f"{self.tier}-{self.jobtype.value}"
            f"-{self.job_category.value}-lv{self.level}"
            f"-passive{self.passive_skill_level}-combat{self.combat_orders_level}"
            f"-union{self.union_block_count}-link{self.link_count}"
        )
        return preset_hash

    def is_buff_duration_preemptive(self) -> bool:
        return self.jobtype in (
            JobType.archmagefb,
            JobType.archmagetc,
            JobType.bishop,
            JobType.luminous,
        )


def add_stats(*stats):
    return sum(stats, Stat())


def add_action_stats(*action_stats):
    return sum(action_stats, ActionStat())


def add_extended_stats(*action_stats):
    return sum(action_stats, ExtendedStat())


def reveal_action_stat(extended_stat: ExtendedStat) -> ActionStat:
    return extended_stat.action_stat.copy()


def preset_optimize_cache_layer(
    setting: SimulationSetting, provider: Callable[[Gearset], Preset], gearset: Gearset
):
    cache_location = f".stat.extended.{setting.get_preset_hash()}.json"

    if setting.cache_root_dir:
        cache_location = os.path.join(setting.cache_root_dir, cache_location)

    if os.path.exists(cache_location):
        return ExtendedStat.parse_file(cache_location)

    preset = provider(gearset)

    extended_stat_value = ExtendedStat(
        stat=preset.get_stat(),
        action_stat=preset.get_action_stat(),
    )

    with open(cache_location, "w", encoding="utf-8") as f:
        json.dump(
            {
                "stat": extended_stat_value.stat.short_dict(),
                "action_stat": extended_stat_value.action_stat.dict(),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    return extended_stat_value


class SimulationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    settings = providers.Factory(SimulationSetting.parse_obj, config)

    passive = providers.Factory(
        get_passive,
        config.jobtype,
        combat_orders_level=config.combat_orders_level,
        passive_skill_level=config.passive_skill_level,
        character_level=config.level,
        weapon_pure_attack_power=config.weapon_pure_attack_power,
    )

    ability_lines = providers.Singleton(
        get_best_ability,
        config.jobtype,
    )

    ability_stat = providers.Factory(
        get_ability_stat,
        ability_lines,
    )

    trait = providers.Factory(
        CharacterTrait,
        ambition=config.trait_level,
        insight=config.trait_level,
        empathy=config.trait_level,
        willpower=config.trait_level,
        diligence=config.trait_level,
        charm=config.trait_level,
    )

    doping = providers.Factory(get_normal_doping)

    monster_life = providers.Factory(get_normal_monsterlife)

    default_extended_stat = providers.Factory(
        add_extended_stats,
        passive,
        doping,
        monster_life,
        ability_stat,
        trait.provided.get_extended_stat.call(),
    )

    gearset = providers.Factory(
        get_baseline_gearset,
        config.tier,
        config.job_category,
        config.jobtype,
    )

    damage_logic = providers.Factory(
        get_damage_logic, config.jobtype, config.combat_orders_level
    )

    preset_optimizer = providers.Factory(
        PresetOptimizer,
        union_block_count=config.union_block_count,
        level=config.level,
        damage_logic=damage_logic,
        character_job_type=config.jobtype,
        alternate_character_job_types=[],
        link_count=config.link_count,
        default_stat=default_extended_stat.provided.stat,
        buff_duration_preempted=settings.provided.is_buff_duration_preemptive.call(),
    )

    optimial_preset = providers.Singleton(
        preset_optimizer.provided.create_optimal_preset_from_gearset.call(gearset),
    )

    preset_cache = providers.Singleton(
        preset_optimize_cache_layer,
        settings,
        preset_optimizer.provided.create_optimal_preset_from_gearset,
        gearset,
    )

    character = providers.Factory(
        add_extended_stats,
        preset_cache,
        default_extended_stat,
    )
    # Use caching

    client_configuration = providers.Factory(get_client_configuration, config.jobtype)

    level_advantage = providers.Factory(
        LevelAdvantage().get_advantage, config.mob_level, config.level
    )

    dpm_calculator = providers.Factory(
        DamageCalculator,
        character_spec=character.provided.stat,
        damage_logic=damage_logic,
        armor=config.armor,
        level_advantage=level_advantage,
        force_advantage=config.force_advantage,
    )

    client_patch_injected_values = providers.Dict(
        character_stat=character.provided.stat,
        character_level=config.level,
        weapon_attack_power=config.weapon_attack_power,
        weapon_pure_attack_power=config.weapon_pure_attack_power,
    )

    client = providers.Singleton(
        get_client,
        character.provided.action_stat,
        client_configuration.provided.get_groups.call(),
        client_patch_injected_values,
        client_configuration.provided.get_filled_v_skill.call(config.v_skill_level),
        client_configuration.provided.get_filled_v_improvements.call(
            config.v_improvements_level
        ),
        passive_skill_level=config.passive_skill_level,
        combat_orders_level=config.combat_orders_level,
    )
