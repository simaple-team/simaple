import json
import os
from typing import Callable

import pydantic
from dependency_injector import containers, providers

from simaple.core import ActionStat, ElementalResistance, JobCategory, JobType, Stat
from simaple.data.baseline import get_baseline_gearset
from simaple.data.client_configuration import get_client_configuration
from simaple.data.damage_logic import get_damage_logic
from simaple.data.doping import get_normal_doping
from simaple.data.monster_life import get_normal_monsterlife_stat
from simaple.data.passive import get_passive_and_default_active_stat
from simaple.gear.gearset import Gearset
from simaple.optimizer.preset import Preset, PresetOptimizer
from simaple.simulate.kms import get_client
from simaple.simulate.report.dpm import DPMCalculator, LevelAdvantage


class SimulationSetting(pydantic.BaseSettings):
    tier: str
    jobtype: JobType
    job_category: JobCategory
    level: int
    action_stat: ActionStat
    use_doping: bool = True
    passive_skill_level: int
    combat_orders_level: int
    union_block_count: int = 37
    link_count: int = 12 + 1
    armor: int = 300
    mob_level: int = 265
    force_advantage: float = 1.0

    v_skill_level: int = 30
    v_improvements_level: int = 60
    elemental_resistance: ElementalResistance

    def get_preset_hash(self) -> str:
        preset_hash = (
            f"{self.tier}-{self.jobtype.value}"
            f"-{self.job_category.value}-lv{self.level}"
            f"-passive{self.passive_skill_level}-combat{self.combat_orders_level}"
            f"-union{self.union_block_count}-link{self.link_count}"
        )
        return preset_hash


def add_stats(*stats):
    return sum(stats, Stat())


def preset_optimize_cache_layer(
    setting: SimulationSetting, provider: Callable[[Gearset], Preset], gearset: Gearset
):
    cache_location = f".stat.{setting.get_preset_hash()}.json"

    if os.path.exists(cache_location):
        return Stat.parse_file(cache_location)

    value = provider(gearset).get_total_stat()
    with open(cache_location, "w", encoding="utf-8") as f:
        json.dump(value.short_dict(), f, ensure_ascii=False, indent=2)

    return value


class SimulationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    settings = providers.Factory(SimulationSetting.parse_obj, config)

    passive_stat = providers.Factory(
        get_passive_and_default_active_stat,
        config.jobtype,
        combat_orders_level=config.combat_orders_level,
        passive_skill_level=config.passive_skill_level,
        character_level=config.level,
    )

    doping_stat = providers.Factory(get_normal_doping)

    monster_life_stat = providers.Factory(get_normal_monsterlife_stat)

    default_stat = providers.Factory(
        add_stats,
        passive_stat,
        doping_stat,
        monster_life_stat,
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
        default_stat=default_stat,
    )

    optimial_preset = providers.Singleton(
        preset_optimizer.provided.create_optimal_preset_from_gearset.call(gearset),
    )

    # Use caching
    character_stat = providers.Factory(
        add_stats,
        providers.Singleton(
            preset_optimize_cache_layer,
            settings,
            preset_optimizer.provided.create_optimal_preset_from_gearset,
            gearset,
        ),
        default_stat,
    )

    client_configuration = providers.Factory(get_client_configuration, config.jobtype)

    level_advantage = providers.Factory(
        LevelAdvantage().get_advantage, config.mob_level, config.level
    )

    dpm_calculator = providers.Factory(
        DPMCalculator,
        character_spec=character_stat,
        damage_logic=damage_logic,
        armor=config.armor,
        level_advantage=level_advantage,
        force_advantage=config.force_advantage,
        elemental_resistance_disadvantage=providers.Factory(
            ElementalResistance.parse_obj,
            config.elemental_resistance,
        ).provided.get_disadvantage.call(),
    )

    client_patch_injected_values = providers.Dict(
        character_stat=character_stat,
        character_level=config.level,
    )

    client = providers.Singleton(
        get_client,
        config.action_stat,
        client_configuration.provided.get_groups.call(),
        client_patch_injected_values,
        client_configuration.provided.get_filled_v_skill.call(config.v_skill_level),
        client_configuration.provided.get_filled_v_improvements.call(
            config.v_improvements_level
        ),
    )
