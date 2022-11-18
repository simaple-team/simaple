# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.job.description import GeneralJobArgument
from simaple.job.spec.patch import SkillLevelPatch
from simaple.simulate.base import (
    Actor,
    AddressedStore,
    Client,
    ConcreteStore,
    Environment,
)
from simaple.simulate.timer import install_timer
from simaple.simulate.util import EventDisplayHandler
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch
from simaple.spec.repository import DirectorySpecRepository


@pytest.fixture(scope="package")
def component_repository():
    return DirectorySpecRepository("simaple/simulate/spec/components")


@pytest.fixture
def archmagefb_client(component_repository):
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
    environment = Environment(store=store)

    for component in components:
        component.add_to_environment(environment)

    actor = Actor()
    client = Client(environment, actor)

    install_timer(client)
    actor.add_handler(EventDisplayHandler())

    return client
