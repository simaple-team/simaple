import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.simulate.base import Action
from simaple.simulate.component.view import Validity, ValidityParentView
from simaple.simulate.reserved_names import Tag
from simaple.simulate.timer import time_elapsing_action


def test_archmage_fb(archmagefb_client):
    schedule = [
        ("메디테이션", "use", 0),
        ("이프리트", "use", 0),
        ("퓨리 오브 이프리트", "use", 0),
        ("포이즌 체인", "use", 0),
        ("플레임 헤이즈", "use", 0),
        ("미스트 이럽션", "use", 0),
        ("플레임 헤이즈", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("미스트 이럽션", "use", 0),
        ("플레임 헤이즈", "use", 0),
        ("도트 퍼니셔", "use", 0),
        ("포이즌 노바", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("미스트 이럽션", "use", 0),
        ("플레임 헤이즈", "use", 0),
    ]

    actions = [Action(name=name, method=method) for name, method, timing in schedule]

    for action in actions:
        events = archmagefb_client.play(action)


def test_validity_view(archmagefb_client):
    archmagefb_client.environment.add_view(
        "Validity", ValidityParentView.build(archmagefb_client.environment)
    )

    views = archmagefb_client.environment.show("Validity")
    for v in views:
        assert isinstance(v, Validity)


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
