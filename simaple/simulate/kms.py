import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.data.passive.patch import SkillLevelPatch
from simaple.data.passive_hyper_skill import get_hyper_skill_patch
from simaple.data.skill.patch import VSkillImprovementPatch
from simaple.simulate.base import AddressedStore, Client, ConcreteStore, Environment
from simaple.simulate.component.base import Component
from simaple.simulate.component.view import (
    BuffParentView,
    KeydownParentView,
    RunningParentView,
    ValidityParentView,
)
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.timer import clock_view, install_timer
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch
from simaple.spec.repository import DirectorySpecRepository


def get_kms_component_repository():
    return DirectorySpecRepository("simaple/data/skill/resources/components")


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
    loader = SpecBasedLoader(get_kms_component_repository())

    store = bare_store(action_stat)

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

    environment = Environment(store=store)
    environment.add_view("clock", clock_view)

    for component in components:
        component.add_to_environment(environment)

    client = Client(environment)

    install_timer(client)

    ValidityParentView.build_and_install(environment, "validity")
    BuffParentView.build_and_install(environment, "buff")
    RunningParentView.build_and_install(environment, "running")
    KeydownParentView.build_and_install(environment, "keydown")

    return client
