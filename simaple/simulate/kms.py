import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.data.passive.patch import SkillLevelPatch
from simaple.data.passive_hyper_skill import get_hyper_skill_patch
from simaple.data.skill import get_kms_skill_loader
from simaple.data.skill.patch import VSkillImprovementPatch
from simaple.simulate.base import AddressedStore, Client, ConcreteStore
from simaple.simulate.builder import ClientBuilder
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


def bare_store(action_stat: ActionStat):
    store = AddressedStore(ConcreteStore())
    GlobalProperty(action_stat).install_global_properties(store)
    return store


def get_client(
    action_stat: ActionStat,
    groups: list[str],
    injected_values: dict,
    skill_levels: dict[str, int],
    v_improvements: dict[str, int],
    combat_orders_level: int = 1,
    passive_skill_level: int = 0,
) -> Client:
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

    client_builder = ClientBuilder(bare_store(action_stat))
    client_builder.add_view("clock", clock_view)

    for component in components:
        client_builder.add_component(component)

    client_builder.add_dispatcher(timer_delay_dispatcher)
    client_builder.add_aggregation_view(InformationParentView, "info")
    client_builder.add_aggregation_view(ValidityParentView, "validity")
    client_builder.add_aggregation_view(BuffParentView, "buff")
    client_builder.add_aggregation_view(RunningParentView, "running")
    client_builder.add_aggregation_view(KeydownParentView, "keydown")

    client = client_builder.build_client()

    return client
