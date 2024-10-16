import simaple.simulate.component.common  # noqa: F401
import simaple.simulate.component.specific  # noqa: F401
from simaple.core.base import ActionStat
from simaple.simulate.builder import EngineBuilder
from simaple.simulate.component.base import Component
from simaple.simulate.component.view import (
    BuffParentView,
    InformationParentView,
    KeydownParentView,
    RunningParentView,
    ValidityParentView,
)
from simaple.simulate.core.store import AddressedStore, ConcreteStore
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.timer import clock_view, timer_delay_dispatcher


def bare_store(action_stat: ActionStat) -> AddressedStore:
    store = AddressedStore(ConcreteStore())
    GlobalProperty(action_stat).install_global_properties(store)
    return store


def get_builder(
    components: list[Component],
    action_stat: ActionStat,
) -> EngineBuilder:
    engine_builder = EngineBuilder(bare_store(action_stat))
    engine_builder.add_view("clock", clock_view)

    for component in components:
        engine_builder.add_component(component)

    engine_builder.add_reducer(timer_delay_dispatcher)

    engine_builder.add_aggregation_view(InformationParentView, "info")
    engine_builder.add_aggregation_view(ValidityParentView, "validity")
    engine_builder.add_aggregation_view(BuffParentView, "buff")
    engine_builder.add_aggregation_view(RunningParentView, "running")
    engine_builder.add_aggregation_view(KeydownParentView, "keydown")

    return engine_builder
