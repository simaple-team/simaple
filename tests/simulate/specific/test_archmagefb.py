import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.core.base import Stat
from simaple.simulate.actor import time_elapsing_action
from simaple.simulate.base import Action
from simaple.simulate.component.view import BuffParentView, Validity, ValidityParentView
from simaple.simulate.reserved_names import Tag


def test_archmage_fb(archmagefb_client):

    schedule = [
        ("메디테이션", "use", None),
        ("이프리트", "use", None),
        ("퓨리 오브 이프리트", "use", None),
        ("포이즌 체인", "use", None),
        ("플레임 헤이즈", "use", None),
        ("미스트 이럽션", "use", None),
        ("플레임 헤이즈", "use", None),
        ("플레임 스윕", "use", None),
        ("플레임 스윕", "use", None),
        ("플레임 스윕", "use", None),
        ("플레임 스윕", "use", None),
        ("플레임 스윕", "use", None),
        ("플레임 스윕", "use", None),
        ("미스트 이럽션", "use", None),
        ("플레임 헤이즈", "use", None),
        ("도트 퍼니셔", "use", None),
        ("포이즌 노바", "use", None),
        ("플레임 스윕", "use", None),
        ("플레임 스윕", "use", None),
        ("미스트 이럽션", "use", None),
        ("플레임 헤이즈", "use", None),
    ]

    actions = [
        Action(name=name, method=method, payload=payload)
        for name, method, payload in schedule
    ]

    for action in actions:
        events = archmagefb_client.play(action)


def test_validity_view(archmagefb_client):
    archmagefb_client.environment.add_view(
        "validity", ValidityParentView.build(archmagefb_client.environment)
    )

    views = archmagefb_client.environment.show("validity")

    for v in views:
        assert isinstance(v, Validity)


def test_buff_view(archmagefb_client):
    archmagefb_client.environment.add_view(
        "buff", BuffParentView.build(archmagefb_client.environment)
    )

    current_buff_stat = archmagefb_client.environment.show("buff")
    assert current_buff_stat == Stat()

    archmagefb_client.play(Action(name="에픽 어드벤처", method="use"))

    assert archmagefb_client.environment.show("buff") == Stat(damage_multiplier=10)


def test_poison_nova(archmagefb_client):
    actions = [
        Action(name="포이즌 노바", method="use"),
        time_elapsing_action(2000),
        Action(name="미스트 이럽션", method="use"),
    ]

    events = []

    for action in actions:
        events += archmagefb_client.play(action)

    assert "포이즌 노바.trigger" in [e.signature for e in events]


def test_poison_chain(archmagefb_client):
    actions = [
        Action(name="포이즌 체인", method="use"),
        time_elapsing_action(25000),
        time_elapsing_action(25000),
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
