import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.core.base import Stat
from simaple.simulate.base import Client, message_signature, Action
from simaple.simulate.reserved_names import Tag


def test_buff_view(archmagefb_client: Client):
    current_buff_stat = archmagefb_client.show("buff")

    archmagefb_client.play(dict(name="에픽 어드벤쳐", method="use", payload=None))

    assert archmagefb_client.show("buff") == current_buff_stat + Stat(
        damage_multiplier=10
    )


def test_poison_nova(archmagefb_client: Client):
    actions: list[Action] = [
        dict(name="포이즌 노바", method="use", payload=None),
        dict(name="*", method="elapse", payload=2000),
        dict(name="미스트 이럽션", method="use", payload=None),
    ]

    events = []

    for action in actions:
        events += archmagefb_client.play(action)

    assert "포이즌 노바.trigger" in [message_signature(e) for e in events]


def test_poison_chain(archmagefb_client: Client):
    actions: list[Action] = [
        dict(name="포이즌 체인", method="use", payload=None),
        dict(name="*", method="elapse", payload=25000),
        dict(name="*", method="elapse", payload=25000),
    ]

    events = []

    for action in actions:
        events += archmagefb_client.play(action)

    damage_events = [e for e in events if e["tag"] == Tag.DAMAGE]

    assert len(damage_events) == 9 + 1

    for idx in range(1, 5):
        assert (
            damage_events[idx + 1]["payload"]["damage"]
            > damage_events[idx]["payload"]["damage"]
        )
