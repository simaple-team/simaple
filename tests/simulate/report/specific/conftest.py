# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.data.passive.patch import SkillLevelPatch
from simaple.data.skill.patch import VSkillImprovementPatch
from simaple.simulate.base import AddressedStore, Client, ConcreteStore, Environment
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.timer import clock_view, install_timer
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch
from simaple.spec.repository import DirectorySpecRepository


@pytest.fixture
def archmagetc_client(component_repository, bare_store):
    loader = SpecBasedLoader(component_repository)

    components = [
        loader.load_all(
            query={"group": group},
            patches=[
                SkillLevelPatch(
                    combat_orders_level=1,
                    passive_skill_level=0,
                    default_skill_levels={},
                ),
                EvalPatch(
                    injected_values={
                        "character_level": 260,
                    }
                ),
                VSkillImprovementPatch(improvements={}),
            ],
        )
        for group in ("archmagetc", "common", "adventurer.magician")
    ]

    components = sum(components, [])

    environment = Environment(store=bare_store)
    environment.add_view("clock", clock_view)

    for component in components:
        component.add_to_environment(environment)

    client = Client(environment)

    install_timer(client)

    # from simaple.simulate.util import EventDisplayHandler
    # client.add_handler(EventDisplayHandler())

    return client
