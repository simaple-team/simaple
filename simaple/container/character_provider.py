import json
import os
from typing import Callable

from simaple.container.simulation import (
    CharacterDependentSimulationConfig,
    CharacterProvidingConfig,
)
from simaple.core import ExtendedStat, JobCategory, JobType
from simaple.data import get_best_ability
from simaple.data.baseline import get_baseline_gearset
from simaple.data.doping import get_normal_doping
from simaple.data.jobs.builtin import get_passive
from simaple.gear.gearset import Gearset
from simaple.optimizer.preset import Preset, PresetOptimizer
from simaple.system.ability import get_ability_stat
from simaple.system.propensity import Propensity


def _is_buff_duration_preemptive(jobtype: JobType) -> bool:
    return jobtype in (
        JobType.archmagefb,
        JobType.archmagetc,
        JobType.bishop,
        JobType.luminous,
    )


def add_extended_stats(*action_stats):
    return sum(action_stats, ExtendedStat())


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


def serialize_character_provider(provider: CharacterProvidingConfig) -> str:
    obj = {
        "config": provider.model_dump_json(),
        "config_name": provider.__class__.__name__,
    }

    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


def deserialize_character_provider(data: str) -> CharacterProvidingConfig:
    obj = json.loads(data)
    config_name = obj["config_name"]
    config = obj["config"]

    if config_name == BaselineSimulationConfig.__name__:
        return BaselineSimulationConfig.model_validate_json(config)

    raise ValueError(f"Unknown config name: {config_name}")
