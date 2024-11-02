from simaple.core.base import ActionStat
from simaple.simulate.component.common.attack_skill import AttackSkillComponent
from simaple.simulate.core.store import AddressedStore, ConcreteStore
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.usecase import Usecase


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

    usecase = Usecase()
    usecase.use_component(attack_skill_1)
    usecase.use_component(attack_skill_2)
    runtime = usecase.create_simulation_runtime(store=store)

    event = runtime.resolve(
        {
            "name": "test-B",
            "method": "use",
            "payload": 3.0,
        }
    )

    print(event)
