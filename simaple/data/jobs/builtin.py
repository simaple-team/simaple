import itertools
from pathlib import Path
from typing import Any, Optional, TypedDict, cast

from simaple.core import JobType
from simaple.core.base import ExtendedStat, Stat
from simaple.core.damage import DamageLogic
from simaple.data.jobs.definitions import BuiltinStrategy
from simaple.data.jobs.definitions.passive import PassiveSkill
from simaple.data.jobs.definitions.skill_profile import SkillProfile
from simaple.data.jobs.patch import (
    HexaSkillImprovementPatch,
    PassiveHyperskillPatch,
    SkillImprovementPatch,
    SkillLevelPatch,
    VSkillImprovementPatch,
)
from simaple.simulate.component.base import Component
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import ArithmeticPatch, Patch
from simaple.spec.repository import DirectorySpecRepository

_BUILTIN_KMS_SKILL_REPOSITORY: DirectorySpecRepository | None = None


def get_kms_spec_resource_path() -> str:
    return str(Path(__file__).parent / "resources")


def get_kms_jobs_repository() -> DirectorySpecRepository:
    global _BUILTIN_KMS_SKILL_REPOSITORY
    if _BUILTIN_KMS_SKILL_REPOSITORY is None:
        _BUILTIN_KMS_SKILL_REPOSITORY = DirectorySpecRepository(
            get_kms_spec_resource_path()
        )

    return _BUILTIN_KMS_SKILL_REPOSITORY


def get_kms_skill_loader() -> SpecBasedLoader:
    return SpecBasedLoader(get_kms_jobs_repository())


def get_skill_profile(jobtype: JobType) -> SkillProfile:
    loader = get_kms_skill_loader()
    return cast(
        SkillProfile,
        loader.load(
            query={"group": jobtype.value, "kind": "SkillProfile"},
        ),
    )


def get_damage_logic(jobtype: JobType, combat_orders_level: int) -> DamageLogic:
    loader = get_kms_skill_loader()
    patches = [
        SkillLevelPatch(
            combat_orders_level=combat_orders_level,
            passive_skill_level=0,
        ),
        ArithmeticPatch(variables={}),
    ]
    return cast(
        DamageLogic,
        loader.load(
            query={"group": jobtype.value, "kind": "DamageLogic"},
            patches=patches,
        ),
    )


def _get_patches_for_passive_skills(
    combat_orders_level: int,
    passive_skill_level: int,
    character_level: int,
    skill_levels: dict[str, int] = {},
    weapon_pure_attack_power: Optional[int] = None,
) -> list[Patch]:
    return [
        SkillLevelPatch(
            combat_orders_level=combat_orders_level,
            passive_skill_level=passive_skill_level,
            default_skill_levels=skill_levels,
        ),
        ArithmeticPatch(
            variables={
                "character_level": character_level,
                "weapon_pure_attack_power": weapon_pure_attack_power,
            }
        ),
    ]


def get_passive(
    jobtype: JobType,
    combat_orders_level: int,
    passive_skill_level: int,
    character_level: int,
    skill_levels: dict[str, int],
    weapon_pure_attack_power: Optional[int] = None,
) -> ExtendedStat:
    skill_profile = get_skill_profile(jobtype)
    loader = get_kms_skill_loader()
    patches = _get_patches_for_passive_skills(
        combat_orders_level,
        passive_skill_level,
        character_level,
        skill_levels,
        weapon_pure_attack_power=weapon_pure_attack_power,
    )
    passive_skills: list[PassiveSkill] = list(
        itertools.chain(
            *[
                loader.load_all(
                    query={"group": group, "kind": "PassiveSkill"}, patches=patches
                )
                for group in skill_profile.get_groups()
            ]
        )
    )

    return sum(
        [passive_skill.get_extended_stat() for passive_skill in passive_skills],
        ExtendedStat(),
    )


def get_builtin_strategy(jobtype: JobType) -> BuiltinStrategy:
    loader = get_kms_skill_loader()
    return cast(
        BuiltinStrategy,
        loader.load(
            query={"group": jobtype.value, "kind": "BuiltinStrategy"},
        ),
    )


class BuilderRequiredExtraVariables(TypedDict):
    character_level: int
    character_stat: Stat
    weapon_attack_power: int
    weapon_pure_attack_power: int
    combat_orders_level: int
    passive_skill_level: int


def _as_reference_variables(
    extra_variables: BuilderRequiredExtraVariables,
) -> dict[str, Any]:
    reference = {
        "character_level": extra_variables["character_level"],
        "weapon_attack_power": extra_variables["weapon_attack_power"],
        "weapon_pure_attack_power": extra_variables["weapon_pure_attack_power"],
        "combat_orders_level": extra_variables["combat_orders_level"],
        "passive_skill_level": extra_variables["passive_skill_level"],
    }
    reference.update(
        {
            f"character_stat.{k}": v
            for k, v in extra_variables["character_stat"].model_dump().items()
        }
    )

    return reference


def _exclude_hexa_skill(
    components: list[Component],
    hexa_replacements: dict[str, str],
    skill_levels: dict[str, int],
) -> list[Component]:
    _component_names = [component.name for component in components]
    components_to_exclude = []

    for low_tier, high_tier in hexa_replacements.items():
        assert low_tier in _component_names, f"{low_tier} is not in {_component_names}"
        assert (
            high_tier in _component_names
        ), f"{high_tier} is not in {_component_names}"

        if skill_levels.get(high_tier, 0) > 0:
            components_to_exclude.append(low_tier)

    components = [
        component
        for component in components
        if component.name not in components_to_exclude
    ]
    return components


def build_skills(
    groups: list[str],
    skill_levels: dict[str, int],
    v_improvements: dict[str, int],
    hexa_improvements: dict[str, int],
    hexa_replacements: dict[str, str],
    injected_values: BuilderRequiredExtraVariables,
) -> list[Component]:
    loader = get_kms_skill_loader()

    reference_variables = _as_reference_variables(injected_values)

    skill_improvements = sum(
        [
            loader.load_all(
                query={"group": group, "kind": "SkillImprovement"},
                patches=[
                    SkillLevelPatch(
                        combat_orders_level=injected_values["combat_orders_level"],
                        passive_skill_level=injected_values["passive_skill_level"],
                        default_skill_levels=skill_levels,
                    ),
                    ArithmeticPatch(variables=reference_variables),
                ],
            )
            for group in groups
        ],
        [],
    )

    component_sets = [
        loader.load_all(
            query={"group": group, "kind": "Component"},
            patches=[
                SkillLevelPatch(
                    combat_orders_level=injected_values["combat_orders_level"],
                    passive_skill_level=injected_values["passive_skill_level"],
                    default_skill_levels=skill_levels,
                ),
                ArithmeticPatch(variables=reference_variables),
                VSkillImprovementPatch(improvements=v_improvements),
                HexaSkillImprovementPatch(improvements=hexa_improvements),
                PassiveHyperskillPatch(
                    hyper_skills=loader.load_all(
                        query={"group": group, "kind": "PassiveHyperskill"},
                    )
                ),
                SkillImprovementPatch(improvements=skill_improvements),
            ],
        )
        for group in groups
    ]

    components: list[Component] = sum(component_sets, [])
    components = _exclude_hexa_skill(components, hexa_replacements, skill_levels)

    return components
