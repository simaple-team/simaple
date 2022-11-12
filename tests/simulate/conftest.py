# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.job.description import GeneralJobArgument
from simaple.job.spec.patch import SkillLevelPatch
from simaple.simulate.base import (
    AddressedStore,
    Client,
    ConcreteStore,
    Environment,
    Relay,
)
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.timer import TimerEventHandler, clock_view, install_timer
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch
from simaple.spec.repository import DirectorySpecRepository


@pytest.fixture(scope="package")
def component_repository():
    return DirectorySpecRepository("simaple/simulate/spec/components")


@pytest.fixture
def global_property():
    return GlobalProperty(ActionStat())


@pytest.fixture
def archmagefb_client(component_repository, global_property):
    loader = SpecBasedLoader(component_repository)

    components = loader.load_all(
        query={"group": "archmagefb"},
        patches=[
            SkillLevelPatch(
                job_argument=GeneralJobArgument(
                    combat_orders_level=1,
                    passive_skill_level=0,
                    character_level=260,
                ),
            ),
            EvalPatch(
                injected_values={
                    "character_level": 260,
                }
            ),
        ],
    )

    store = AddressedStore(ConcreteStore())
    global_property.install_global_properties(store)

    environment = Environment(store=store)
    environment.add_view("clock", clock_view)

    for component in components:
        component.add_to_environment(environment)

    relay = Relay()
    relay.add_handler(TimerEventHandler())

    client = Client(environment, relay)

    install_timer(client)

    # relay.add_handler(EventDisplayHandler())

    return client
