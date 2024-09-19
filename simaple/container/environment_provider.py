import json
from abc import ABCMeta, abstractmethod
from typing import Any, Type

import pydantic

from simaple.container.simulation import SimulationEnvironment
from simaple.core import ActionStat, ExtendedStat, JobType, Stat
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


class MemoizableEnvironment(pydantic.BaseModel):
    passive_skill_level: int
    combat_orders_level: int
    weapon_pure_attack_power: int

    jobtype: JobType
    level: int

    character: ExtendedStat


class EnvironmentProvider(pydantic.BaseModel, metaclass=ABCMeta):
    """
    EnvironmentProvider provides a SimulationEnvironment from some
    `abstract` configuration, which is better readable and sustainable.
    """

    @abstractmethod
    def get_simulation_environment(self) -> SimulationEnvironment: ...

    @classmethod
    def get_name(cls):
        return cls.__name__


class MemoizableEnvironmentProvider(EnvironmentProvider):
    """
    MemoizableEnvironmentProvider provides `memoization` interface
    for computation-extensive environment providers.
    """

    @abstractmethod
    def get_memoizable_environment(
        self,
    ) -> dict[str, Any]: ...

    @abstractmethod
    def get_memoization_independent_environment(
        self,
    ) -> dict[str, Any]: ...

    @abstractmethod
    def get_memoization_key(self) -> str: ...

    def get_simulation_environment(
        self,
    ) -> SimulationEnvironment:
        environment_dict = self.get_memoization_independent_environment()
        environment_dict.update(self.get_memoizable_environment())

        environment = SimulationEnvironment.model_validate(environment_dict)
        return environment


class MinimalEnvironmentProvider(MemoizableEnvironmentProvider):
    level: int
    action_stat: ActionStat
    stat: Stat
    jobtype: JobType

    weapon_pure_attack_power: int = 0
    combat_orders_level: int = 1

    # Below are memoization-independent environment
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

    def character(self) -> ExtendedStat:
        return ExtendedStat(
            stat=self.stat,
            action_stat=self.action_stat,
        )

    def get_memoization_independent_environment(
        self,
    ) -> dict[str, Any]:
        return self.model_dump(
            include={
                "use_doping",
                "armor",
                "mob_level",
                "force_advantage",
                "v_skill_level",
                "hexa_skill_level",
                "hexa_mastery_level",
                "v_improvements_level",
                "hexa_improvements_level",
                "weapon_attack_power",
            }
        )

    def get_memoizable_environment(
        self,
    ) -> dict[str, Any]:
        return MemoizableEnvironment(
            passive_skill_level=0,
            combat_orders_level=self.combat_orders_level,
            weapon_pure_attack_power=self.weapon_pure_attack_power,
            jobtype=self.jobtype,
            level=self.level,
            character=self.character(),
        ).model_dump()

    def get_memoization_key(self) -> str:
        return json.dumps(
            json.loads(
                self.model_dump_json(
                    exclude={
                        "use_doping",
                        "armor",
                        "mob_level",
                        "force_advantage",
                        "v_skill_level",
                        "hexa_skill_level",
                        "hexa_mastery_level",
                        "v_improvements_level",
                        "hexa_improvements_level",
                        "weapon_attack_power",
                    },
                )
            ),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )


class BaselineEnvironmentProvider(MemoizableEnvironmentProvider):
    tier: str
    union_block_count: int = 37
    link_count: int = 12 + 1
    artifact_level: int
    propensity_level: int = 100

    jobtype: JobType
    level: int

    passive_skill_level: int
    combat_orders_level: int
    weapon_pure_attack_power: int = 0

    # Below are memoization-independent environment
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

    def get_memoization_independent_environment(
        self,
    ) -> dict[str, Any]:
        return self.model_dump(
            include={
                "use_doping",
                "armor",
                "mob_level",
                "force_advantage",
                "v_skill_level",
                "hexa_skill_level",
                "hexa_mastery_level",
                "v_improvements_level",
                "hexa_improvements_level",
                "weapon_attack_power",
            }
        )

    def get_memoization_key(self) -> str:
        return json.dumps(
            json.loads(
                self.model_dump_json(
                    exclude={
                        "use_doping",
                        "armor",
                        "mob_level",
                        "force_advantage",
                        "v_skill_level",
                        "hexa_skill_level",
                        "hexa_mastery_level",
                        "v_improvements_level",
                        "hexa_improvements_level",
                        "weapon_attack_power",
                    },
                )
            ),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

    def get_memoizable_environment(
        self,
    ) -> dict[str, Any]:
        return MemoizableEnvironment(
            passive_skill_level=self.passive_skill_level,
            combat_orders_level=self.combat_orders_level,
            weapon_pure_attack_power=self.weapon_pure_attack_power,
            jobtype=self.jobtype,
            level=self.level,
            character=self.character(),
        ).model_dump()

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

    def gearset(self):
        return get_baseline_gearset(
            self.tier,
            self.jobtype,
        )

    def preset_optimizer(self):
        damage_logic = get_damage_logic(self.jobtype, self.combat_orders_level)
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


_environment_providers: dict[str, Type[EnvironmentProvider]] = {
    BaselineEnvironmentProvider.__name__: BaselineEnvironmentProvider,
    MinimalEnvironmentProvider.__name__: MinimalEnvironmentProvider,
}


def get_environment_provider(name: str, config: dict) -> EnvironmentProvider:
    return _environment_providers[name].model_validate(config)
