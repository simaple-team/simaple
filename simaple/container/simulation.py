import json
import os
from typing import Callable, cast

import pydantic

from simaple.core import ExtendedStat, JobCategory, JobType
from simaple.data.ability import get_best_ability
from simaple.data.baseline import get_baseline_gearset
from simaple.data.builtin_strategy import get_builtin_strategy
from simaple.data.damage_logic import get_damage_logic
from simaple.data.doping import get_normal_doping
from simaple.data.passive import get_passive
from simaple.data.skill_profile import get_skill_profile
from simaple.gear.gearset import Gearset
from simaple.optimizer.preset import Preset, PresetOptimizer
from simaple.simulate.engine import MonotonicEngine, OperationEngine
from simaple.simulate.kms import get_builder
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage
from simaple.system.ability import get_ability_stat
from simaple.system.propensity import Propensity


class SimulationSetting(pydantic.BaseModel):
    tier: str
    jobtype: JobType
    job_category: JobCategory
    level: int

    use_doping: bool = True
    passive_skill_level: int
    combat_orders_level: int
    union_block_count: int = 37
    link_count: int = 12 + 1
    artifact_level: int
    armor: int = 300
    mob_level: int = 265
    force_advantage: float = 1.0
    propensity_level: int = 100

    v_skill_level: int = 30
    hexa_skill_level: int = 1
    hexa_mastery_level: int = 1
    v_improvements_level: int = 60
    hexa_improvements_level: int = 0

    weapon_attack_power: int = 0
    weapon_pure_attack_power: int = 0

    cache_root_dir: str = ".simaple"

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


def add_extended_stats(*action_stats):
    return sum(action_stats, ExtendedStat())


def preset_optimize_cache_layer(
    setting: SimulationSetting, provider: Callable[[Gearset], Preset], gearset: Gearset
):
    cache_location = f".stat.extended.{setting.get_preset_hash()}.json"

    if setting.cache_root_dir:
        if not os.path.exists(setting.cache_root_dir):
            os.makedirs(setting.cache_root_dir)

        cache_location = os.path.join(setting.cache_root_dir, cache_location)

    if os.path.exists(cache_location):
        with open(cache_location, encoding="utf-8") as f:
            cache = json.load(f)
        return ExtendedStat.model_validate(cache)

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


class SimulationContainer:
    def __init__(self, setting: SimulationSetting) -> None:
        self.setting = setting

    def config(self) -> SimulationSetting:
        return self.setting

    def passive(self) -> ExtendedStat:
        config = self.config()

        return get_passive(
            config.jobtype,
            combat_orders_level=config.combat_orders_level,
            passive_skill_level=config.passive_skill_level,
            character_level=config.level,
            weapon_pure_attack_power=config.weapon_pure_attack_power,
        )

    def ability_lines(self):
        config = self.config()
        return get_best_ability(config.jobtype)

    def ability_stat(self):
        ability_lines = self.ability_lines()
        return get_ability_stat(ability_lines)

    def propensity(self):
        config = self.config()
        return Propensity(
            ambition=config.propensity_level,
            insight=config.propensity_level,
            empathy=config.propensity_level,
            willpower=config.propensity_level,
            diligence=config.propensity_level,
            charm=config.propensity_level,
        )

    def doping(self):
        return get_normal_doping()

    def default_extended_stat(self):
        passive = self.passive()
        doping = self.doping()
        ability_stat = self.ability_stat()
        propensity = self.propensity()

        return add_extended_stats(
            passive,
            doping,
            ability_stat,
            propensity.get_extended_stat(),
        )

    def gearset(self):
        config = self.config()
        return get_baseline_gearset(
            config.tier,
            config.job_category,
            config.jobtype,
        )

    def damage_logic(self):
        config = self.config()
        return get_damage_logic(config.jobtype, config.combat_orders_level)

    def preset_optimizer(self):
        config = self.config()
        damage_logic = self.damage_logic()
        default_extended_stat = self.default_extended_stat()
        config = self.config()
        return PresetOptimizer(
            union_block_count=config.union_block_count,
            level=config.level,
            damage_logic=damage_logic,
            character_job_type=config.jobtype,
            alternate_character_job_types=[],
            link_count=config.link_count,
            default_stat=default_extended_stat.stat,
            buff_duration_preempted=config.is_buff_duration_preemptive(),
            artifact_level=config.artifact_level,
        )

    def optimial_preset(self):
        preset_optimizer = self.preset_optimizer()
        gearset = self.gearset()
        return preset_optimizer.create_optimal_preset_from_gearset(
            gearset,
        )

    def preset_cache(self):
        config = self.config()
        preset_optimizer = self.preset_optimizer()
        gearset = self.gearset()
        return preset_optimize_cache_layer(
            config,
            preset_optimizer.create_optimal_preset_from_gearset,
            gearset,
        )

    def character(self):
        preset_cache = self.preset_cache()
        default_extended_stat = self.default_extended_stat()
        return add_extended_stats(
            preset_cache,
            default_extended_stat,
        )

    def skill_profile(self):
        config = self.config()
        return get_skill_profile(config.jobtype)

    def builtin_strategy(self):
        config = self.config()
        return get_builtin_strategy(config.jobtype)

    def level_advantage(self):
        config = self.config()
        return LevelAdvantage().get_advantage(
            config.mob_level,
            config.level,
        )

    def dpm_calculator(self) -> DamageCalculator:
        character = self.character()
        damage_logic = self.damage_logic()
        config = self.config()
        level_advantage = self.level_advantage()

        return DamageCalculator(
            character_spec=character.stat,
            damage_logic=damage_logic,
            armor=config.armor,
            level_advantage=level_advantage,
            force_advantage=config.force_advantage,
        )

    def builder(self):
        skill_profile = self.skill_profile()
        config = self.config()
        character = self.character()
        return get_builder(
            skill_profile.get_groups(),
            skill_profile.get_skill_levels(
                config.v_skill_level,
                config.hexa_skill_level,
                config.hexa_mastery_level,
            ),
            skill_profile.get_filled_v_improvements(config.v_improvements_level),
            skill_profile.get_filled_hexa_improvements(config.hexa_improvements_level),
            skill_profile.get_skill_replacements(),
            {
                "character_stat": character.stat,
                "character_level": config.level,
                "weapon_attack_power": config.weapon_attack_power,
                "weapon_pure_attack_power": config.weapon_pure_attack_power,
                "action_stat": character.action_stat,
                "passive_skill_level": config.passive_skill_level,
                "combat_orders_level": config.combat_orders_level,
            },
        )

    def monotonic_engine(self) -> MonotonicEngine:
        builder = self.builder()
        return cast(MonotonicEngine, builder.build_monotonic_engine())

    def operation_engine(self) -> OperationEngine:
        builder = self.builder()
        return cast(OperationEngine, builder.build_operation_engine())
