import pydantic

from simaple.core import ActionStat, JobType, Stat
from simaple.data.jobs import get_skill_profile
from simaple.data.jobs.builtin import build_skills, get_damage_logic
from simaple.simulate.component.base import Component
from simaple.simulate.engine import OperationEngine
from simaple.simulate.kms import get_builder
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage


class FinalCharacterStat(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    stat: Stat
    action_stat: ActionStat

    active_buffs: dict[str, Stat]


class SimulationEnvironment(pydantic.BaseModel):
    """
    SimulationSetting defines complete set of configuration
    to configure Simulation Engine.
    """

    model_config = pydantic.ConfigDict(extra="forbid")

    use_doping: bool = True

    armor: int = 300
    mob_level: int = 265
    force_advantage: float = 1.0

    v_skill_level: int = 30
    v_improvements_level: int = 60

    skill_levels: dict[str, int] = {}
    hexa_improvement_levels: dict[str, int] = {}

    weapon_attack_power: int = 0

    passive_skill_level: int
    combat_orders_level: int
    weapon_pure_attack_power: int

    jobtype: JobType
    level: int
    character: FinalCharacterStat


def get_damage_calculator(environment: SimulationEnvironment) -> DamageCalculator:
    damage_logic = get_damage_logic(
        environment.jobtype, environment.combat_orders_level
    )
    level_advantage = LevelAdvantage().get_advantage(
        environment.mob_level,
        environment.level,
    )

    return DamageCalculator(
        character_spec=environment.character.stat,
        damage_logic=damage_logic,
        armor=environment.armor,
        level_advantage=level_advantage,
        force_advantage=environment.force_advantage,
    )


def get_skill_components(environment: SimulationEnvironment) -> list[Component]:
    skill_profile = get_skill_profile(environment.jobtype)

    possible_skill_names = (
        skill_profile.v_skill_names
        + skill_profile.hexa_skill_names
        + list(skill_profile.hexa_mastery.values())
    )
    for skill_name in environment.skill_levels:
        assert (
            skill_name in possible_skill_names
        ), f"Given explicit skill name \
passed to level: {skill_name} is not in {possible_skill_names}"

    for hexa_improvement_name in environment.hexa_improvement_levels:
        assert (
            hexa_improvement_name in skill_profile.hexa_improvement_names
        ), f"Given explicit \
improvement name passed to level: {hexa_improvement_name} is not in {skill_profile.hexa_improvement_names}"

    return build_skills(
        skill_profile.get_groups(),
        environment.skill_levels,
        skill_profile.get_filled_v_improvements(environment.v_improvements_level),
        environment.hexa_improvement_levels,
        skill_profile.get_skill_replacements(),
        {
            "character_stat": environment.character.stat,
            "character_level": environment.level,
            "weapon_attack_power": environment.weapon_attack_power,
            "weapon_pure_attack_power": environment.weapon_pure_attack_power,
            "passive_skill_level": environment.passive_skill_level,
            "combat_orders_level": environment.combat_orders_level,
        },
    )


def get_operation_engine(environment: SimulationEnvironment) -> OperationEngine:
    skills = get_skill_components(environment)
    builder = get_builder(skills, environment.character.action_stat)
    return builder.build_operation_engine()
