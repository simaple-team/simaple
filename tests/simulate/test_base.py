from simaple.simulate.base import Action, AddressedStore, ConcreteStore, Environment
from simaple.simulate.component.skill import AttackSkillComponent


def test_scenario():
    store = AddressedStore(ConcreteStore())

    attack_skill_1 = AttackSkillComponent(
        name="test-A", damage=300, hit=4, cooldown=14.0, delay=0.0
    )

    attack_skill_2 = AttackSkillComponent(
        name="test-B", damage=400, hit=6, cooldown=14.0, delay=0.0
    )

    environment = Environment(store)
    attack_skill_1.add_to_environment(environment)
    attack_skill_2.add_to_environment(environment)
    print(".")
    event = environment.resolve(
        Action(
            name="test-A",
            method="use",
            payload=None,
        )
    )
    print(event)

    event = environment.resolve(
        Action(
            name="test-B",
            method="use",
            payload=None,
        )
    )
    print(event)

    event = environment.resolve(
        Action(
            name="test-B",
            method="elapse",
            payload=3.0,
        )
    )
    print(event)
