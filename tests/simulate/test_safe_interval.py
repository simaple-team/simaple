from simaple.core.base import ActionStat
from simaple.simulate.builder import EngineBuilder
from simaple.simulate.component.common.attack_skill import AttackSkillComponent
from simaple.simulate.core.base import AddressedStore, ConcreteStore
from simaple.simulate.global_property import GlobalProperty


def test_scenario():
    store = AddressedStore(ConcreteStore())
    global_property = GlobalProperty(ActionStat())
    global_property.install_global_properties(store)

    attack_skill_1 = AttackSkillComponent(
        name="test-A", damage=300, hit=4, cooldown_duration=14.0, delay=0.0, id="test"
    )

    attack_skill_2 = AttackSkillComponent(
        name="test-B", damage=400, hit=6, cooldown_duration=10.0, delay=0.0, id="test"
    )

    runtime = (
        EngineBuilder(store)
        .add_component(attack_skill_1)
        .add_component(attack_skill_2)
        .build_simulation_runtime()
    )

    event = runtime.resolve(
        dict(
            name="test-B",
            method="elapse",
            payload=3.0,
        )
    )

    print(event)
