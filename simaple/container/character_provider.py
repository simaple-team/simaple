import json
from abc import ABCMeta, abstractmethod
from typing import Type

import pydantic

from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core import ActionStat, ExtendedStat, JobCategory, JobType, Stat
from simaple.data import get_best_ability
from simaple.data.baseline import get_baseline_gearset
from simaple.data.doping import get_normal_doping
from simaple.data.jobs.builtin import get_damage_logic, get_passive
from simaple.optimizer.preset import PresetOptimizer
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


class SimulationEnvironmentForCharacterProvider(pydantic.BaseModel):
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


class CharacterDependentEnvironmentForCharacterProvider(pydantic.BaseModel):
    passive_skill_level: int
    combat_orders_level: int
    weapon_pure_attack_power: int

    jobtype: JobType
    level: int

    def damage_logic(self):
        return get_damage_logic(self.jobtype, self.combat_orders_level)


class CharacterProvider(pydantic.BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def character(self) -> ExtendedStat: ...

    @abstractmethod
    def get_character_dependent_simulation_config(
        self,
    ) -> CharacterDependentEnvironmentForCharacterProvider: ...

    @classmethod
    def get_name(cls):
        return cls.__name__

    def get_simulation_container(
        self, confined_environment: SimulationEnvironmentForCharacterProvider
    ):
        environment = confined_environment.model_dump()
        environment.update(
            self.get_character_dependent_simulation_config().model_dump()
        )
        environment["character"] = self.character().model_dump()

        setting = SimulationSetting.model_validate(environment)
        return SimulationContainer(setting)


class MinimalCharacterProvider(CharacterProvider):
    level: int
    action_stat: ActionStat
    stat: Stat
    jobtype: JobType
    job_category: JobCategory

    weapon_pure_attack_power: int = 0
    combat_orders_level: int = 1

    def get_character_dependent_simulation_config(
        self,
    ) -> CharacterDependentEnvironmentForCharacterProvider:
        return CharacterDependentEnvironmentForCharacterProvider(
            passive_skill_level=0,
            combat_orders_level=self.combat_orders_level,
            weapon_pure_attack_power=self.weapon_pure_attack_power,
            jobtype=self.jobtype,
            level=self.level,
        )

    def character(self) -> ExtendedStat:
        return ExtendedStat(
            stat=self.stat,
            action_stat=self.action_stat,
        )


class BaselineCharacterProvider(CharacterProvider):
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
    ) -> CharacterDependentEnvironmentForCharacterProvider:
        return CharacterDependentEnvironmentForCharacterProvider(
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

    def character(self):
        preset_optimizer = self.preset_optimizer()
        gearset = self.gearset()

        preset = preset_optimizer.create_optimal_preset_from_gearset(gearset)

        extended_stat_value = ExtendedStat(
            stat=preset.get_stat(),
            action_stat=preset.get_action_stat(),
        )
        default_extended_stat = self.default_extended_stat()
        return add_extended_stats(
            extended_stat_value,
            default_extended_stat,
        )


_character_providers: dict[str, Type[CharacterProvider]] = {
    BaselineCharacterProvider.__name__: BaselineCharacterProvider,
    MinimalCharacterProvider.__name__: MinimalCharacterProvider,
}


def get_character_provider(name: str, config: dict) -> CharacterProvider:
    return _character_providers[name].model_validate(config)


def serialize_character_provider(provider: CharacterProvider) -> str:
    obj = {
        "config": provider.model_dump_json(),
        "config_name": provider.get_name(),
    }

    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


def deserialize_character_provider(data: str) -> CharacterProvider:
    obj = json.loads(data)
    config_name = obj["config_name"]
    config = obj["config"]

    if config_name == BaselineCharacterProvider.__name__:
        return BaselineCharacterProvider.model_validate_json(config)

    raise ValueError(f"Unknown config name: {config_name}")
