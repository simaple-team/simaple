import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.data.passive.patch import SkillLevelPatch
from simaple.data.passive_hyper_skill import get_hyper_skill_patch
from simaple.data.skill import get_kms_skill_loader
from simaple.data.skill.patch import VSkillImprovementPatch
from simaple.simulate.base import AddressedStore, ConcreteStore
from simaple.simulate.builder import EngineBuilder
from simaple.simulate.component.base import Component
from simaple.simulate.component.view import (
    BuffParentView,
    InformationParentView,
    KeydownParentView,
    RunningParentView,
    ValidityParentView,
)
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.timer import clock_view, timer_delay_dispatcher
from simaple.spec.patch import EvalPatch


def bare_store(action_stat: ActionStat) -> AddressedStore:
    store = AddressedStore(ConcreteStore())
    GlobalProperty(action_stat).install_global_properties(store)
    return store


def get_builder(
    action_stat: ActionStat,
    groups: list[str],
    injected_values: dict,
    skill_levels: dict[str, int],
    v_improvements: dict[str, int],
    combat_orders_level: int = 1,
    passive_skill_level: int = 0,
) -> EngineBuilder:
    loader = get_kms_skill_loader()

    component_sets = [
        loader.load_all(
            query={"group": group},
            patches=[
                SkillLevelPatch(
                    combat_orders_level=combat_orders_level,
                    passive_skill_level=passive_skill_level,
                    default_skill_levels=skill_levels,
                ),
                EvalPatch(injected_values=injected_values),
                VSkillImprovementPatch(improvements=v_improvements),
                get_hyper_skill_patch(group),
            ],
        )
        for group in groups
    ]

    components: list[Component] = sum(component_sets, [])

    engine_builder = EngineBuilder(bare_store(action_stat))
    engine_builder.add_view("clock", clock_view)

    for component in components:
        engine_builder.add_component(component)

    engine_builder.add_dispatcher(timer_delay_dispatcher)
    engine_builder.add_aggregation_view(InformationParentView, "info")
    engine_builder.add_aggregation_view(ValidityParentView, "validity")
    engine_builder.add_aggregation_view(BuffParentView, "buff")
    engine_builder.add_aggregation_view(RunningParentView, "running")
    engine_builder.add_aggregation_view(KeydownParentView, "keydown")

    return engine_builder
