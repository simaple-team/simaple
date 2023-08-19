import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.core.base import Stat
from simaple.simulate.base import Action
from simaple.simulate.component.view import BuffParentView
from simaple.simulate.reserved_names import Tag


def test_buff_view(archmagefb_client):
    archmagefb_client.environment.add_view(
        "buff", BuffParentView.build(archmagefb_client.environment)
    )

    current_buff_stat = archmagefb_client.environment.show("buff")

    archmagefb_client.play(Action(name="에픽 어드벤쳐", method="use"))

    assert archmagefb_client.environment.show("buff") == current_buff_stat + Stat(
        damage_multiplier=10
    )


def test_poison_nova(archmagefb_client):
    actions = [
        Action(name="포이즌 노바", method="use"),
        Action(name="*", method="elapse", payload=2000),
        Action(name="미스트 이럽션", method="use"),
    ]

    events = []

    for action in actions:
        events += archmagefb_client.play(action)

    assert "포이즌 노바.trigger" in [e.signature for e in events]


def test_poison_chain(archmagefb_client):
    actions = [
        Action(name="포이즌 체인", method="use"),
        Action(name="*", method="elapse", payload=25000),
        Action(name="*", method="elapse", payload=25000),
    ]

    events = []

    for action in actions:
        events += archmagefb_client.play(action)

    damage_events = [e for e in events if e.tag == Tag.DAMAGE]

    assert len(damage_events) == 9 + 1

    for idx in range(1, 5):
        assert (
            damage_events[idx + 1].payload["damage"]
            > damage_events[idx].payload["damage"]
        )
