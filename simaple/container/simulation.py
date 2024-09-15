import json
import os
from typing import Callable, cast

import pydantic
from abc import ABCMeta, abstractmethod

from simaple.core import ExtendedStat, JobCategory, JobType
from simaple.data import get_best_ability
from simaple.data.baseline import get_baseline_gearset
from simaple.data.doping import get_normal_doping
from simaple.data.jobs import get_skill_profile
from simaple.data.jobs.builtin import (
    get_builtin_strategy,
    get_damage_logic,
    get_passive,
)
from simaple.gear.gearset import Gearset
from simaple.optimizer.preset import Preset, PresetOptimizer
from simaple.simulate.base import SimulationRuntime
from simaple.simulate.engine import OperationEngine
from simaple.simulate.kms import get_builder
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage
from simaple.system.ability import get_ability_stat
from simaple.system.propensity import Propensity


def add_extended_stats(*action_stats):
    return sum(action_stats, ExtendedStat())


class CharacterDependentSimulationConfig(pydantic.BaseModel):
    passive_skill_level: int
    combat_orders_level: int
    weapon_pure_attack_power: int

    jobtype: JobType
    level: int

    def damage_logic(self):
        return get_damage_logic(self.jobtype, self.combat_orders_level)


def _is_buff_duration_preemptive(jobtype: JobType) -> bool:
    return jobtype in (
        JobType.archmagefb,
        JobType.archmagetc,
        JobType.bishop,
        JobType.luminous,
    )


class CharacterProvidingConfig(pydantic.BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def character(self) -> ExtendedStat: ...

    @abstractmethod
    def get_character_dependent_simulation_config(
        self,
    ) -> CharacterDependentSimulationConfig: ...


class BaselineSimulationConfig(CharacterProvidingConfig):
    tier: str
    union_block_count: int = 37
    link_count: int = 12 + 1
    artifact_level: int
    propensity_level: int = 100

    jobtype: JobType
    job_category: JobCategory
    level: int

    passive_skill_level: int
    combat_orders_level: int
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

    def ability_lines(self):
        return get_best_ability(self.jobtype)

    def ability_stat(self):
        ability_lines = self.ability_lines()
        return get_ability_stat(ability_lines)

    def propensity(self):
        return Propensity(
            ambition=self.propensity_level,
            insight=self.propensity_level,
            empathy=self.propensity_level,
            willpower=self.propensity_level,
            diligence=self.propensity_level,
            charm=self.propensity_level,
        )

    def doping(self):
        return get_normal_doping()

    def passive(self) -> ExtendedStat:
        return get_passive(
            self.jobtype,
            combat_orders_level=self.combat_orders_level,
            passive_skill_level=self.passive_skill_level,
            character_level=self.level,
            weapon_pure_attack_power=self.weapon_pure_attack_power,
        )

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

    def get_character_dependent_simulation_config(
        self,
    ) -> CharacterDependentSimulationConfig:
        return CharacterDependentSimulationConfig(
            passive_skill_level=self.passive_skill_level,
            combat_orders_level=self.combat_orders_level,
            weapon_pure_attack_power=self.weapon_pure_attack_power,
            jobtype=self.jobtype,
            level=self.level,
        )

    def gearset(self):
        return get_baseline_gearset(
            self.tier,
            self.job_category,
            self.jobtype,
        )

    def damage_logic(self):
        return self.get_character_dependent_simulation_config().damage_logic()

    def preset_optimizer(self):
        damage_logic = self.damage_logic()
        default_extended_stat = self.default_extended_stat()
        return PresetOptimizer(
            union_block_count=self.union_block_count,
            level=self.level,
            damage_logic=damage_logic,
            character_job_type=self.jobtype,
            alternate_character_job_types=[],
            link_count=self.link_count,
            default_stat=default_extended_stat.stat,
            buff_duration_preempted=_is_buff_duration_preemptive(self.jobtype),
            artifact_level=self.artifact_level,
        )

    def optimial_preset(self):
        preset_optimizer = self.preset_optimizer()
        gearset = self.gearset()
        return preset_optimizer.create_optimal_preset_from_gearset(
            gearset,
        )

    def preset_cache(self):
        preset_optimizer = self.preset_optimizer()
        gearset = self.gearset()
        return preset_optimize_cache_layer(
            self,
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


class SimulationSetting(pydantic.BaseModel):
    use_doping: bool = True

    armor: int = 300
    mob_level: int = 265
    force_advantage: float = 1.0

    v_skill_level: int = 30
    hexa_skill_level: int = 1
    hexa_mastery_level: int = 1
    v_improvements_level: int = 60
    hexa_improvements_level: int = 0

    weapon_attack_power: int = 0


def preset_optimize_cache_layer(
    setting: BaselineSimulationConfig,
    provider: Callable[[Gearset], Preset],
    gearset: Gearset,
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
    def __init__(
        self, setting: SimulationSetting, character_provider: CharacterProvidingConfig
    ) -> None:
        self.setting = setting
        self.character_provider = character_provider

    def config(self) -> CharacterProvidingConfig:
        return self.character_provider

    def skill_profile(self):
        config = self.config()
        return get_skill_profile(
            config.get_character_dependent_simulation_config().jobtype
        )

    def builtin_strategy(self):
        return get_builtin_strategy(
            self.character_provider.get_character_dependent_simulation_config().jobtype
        )

    def level_advantage(self):
        config = self.setting
        return LevelAdvantage().get_advantage(
            config.mob_level,
            self.character_provider.get_character_dependent_simulation_config().level,
        )

    def dpm_calculator(self) -> DamageCalculator:
        config = self.setting

        character = self.character_provider.character()
        damage_logic = (
            self.character_provider.get_character_dependent_simulation_config().damage_logic()
        )
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
        config = self.setting
        character = self.character_provider.character()
        character_dependent_simulation_setting = (
            self.character_provider.get_character_dependent_simulation_config()
        )

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
                "character_level": character_dependent_simulation_setting.level,
                "weapon_attack_power": config.weapon_attack_power,
                "weapon_pure_attack_power": character_dependent_simulation_setting.weapon_pure_attack_power,
                "action_stat": character.action_stat,
                "passive_skill_level": character_dependent_simulation_setting.passive_skill_level,
                "combat_orders_level": character_dependent_simulation_setting.combat_orders_level,
            },
        )

    def simulation_runtime(self) -> SimulationRuntime:
        builder = self.builder()
        return cast(SimulationRuntime, builder.build_simulation_runtime())

    def operation_engine(self) -> OperationEngine:
        builder = self.builder()
        return cast(OperationEngine, builder.build_operation_engine())
