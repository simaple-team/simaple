from simaple.simulate.base import (
    Action,
    AddressedStore,
    ConcreteStore,
    Reducer,
)
from simaple.simulate.components.skill import AttackSkillComponent


def test_scenario():
    store = AddressedStore(ConcreteStore())

    attack_skill_1 = AttackSkillComponent(
        name="test-A", damage=300, hit=4, cooldown=14.0, delay=0.0
    )

    attack_skill_2 = AttackSkillComponent(
        name="test-B", damage=400, hit=6, cooldown=14.0, delay=0.0
    )

    reducer = Reducer(store)
    attack_skill_1.add_to_reducer(reducer)
    attack_skill_2.add_to_reducer(reducer)
    print(".")
    event = reducer.resolve(
        Action(
            name="test-A",
            method="use",
            payload=None,
        )
    )
    print(event)

    event = reducer.resolve(
        Action(
            name="test-B",
            method="use",
            payload=None,
        )
    )
    print(event)

    print(store._concrete_store._states)

    event = reducer.resolve(
        Action(
            name="test-B",
            method="elapse",
            payload=3.0,
        )
    )
    print(event)

    print(store._concrete_store._states)
