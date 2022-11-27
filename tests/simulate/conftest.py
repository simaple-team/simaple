# pylint: disable=W0621
import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
import simaple.simulate.component.specific  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.data.passive.patch import SkillLevelPatch, VSkillImprovementPatch
from simaple.simulate.base import AddressedStore, Client, ConcreteStore, Environment
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.timer import clock_view, install_timer
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
def bare_store(global_property):
    store = AddressedStore(ConcreteStore())
    global_property.install_global_properties(store)
    return store


@pytest.fixture
def archmagefb_client(component_repository, bare_store):
    loader = SpecBasedLoader(component_repository)

    components = [
        loader.load_all(
            query={"group": group},
            patches=[
                SkillLevelPatch(
                    combat_orders_level=1,
                    passive_skill_level=0,
                    default_skill_levels={
                        "도트 퍼니셔": 30,
                        "포이즌 노바": 30,
                        "오버로드 마나": 30,
                        "포이즌 체인": 30,
                        "퓨리 오브 이프리트": 30,
                    },
                ),
                EvalPatch(
                    injected_values={
                        "character_level": 260,
                    }
                ),
                VSkillImprovementPatch(
                    improvements={
                        "플레임 스윕": 60,
                        "미스트 이럽션": 60,
                        "플레임 헤이즈": 60,
                        "메기도 플레임": 60,
                        "이그나이트": 60,
                        "파이어 오라": 60,
                        "이프리트": 60,
                    }
                ),
            ],
        )
        for group in ("archmagefb", "common", "adventurer.magician")
    ]

    components = sum(components, [])

    environment = Environment(store=bare_store)
    environment.add_view("clock", clock_view)

    for component in components:
        component.add_to_environment(environment)

    client = Client(environment)

    install_timer(client)

    # relay.add_handler(EventDisplayHandler())

    return client
