import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.job.description import GeneralJobArgument
from simaple.job.spec.patch import SkillLevelPatch
from simaple.simulate.base import (
    Action,
    Actor,
    AddressedStore,
    Client,
    ConcreteStore,
    Reducer,
)
from simaple.simulate.timer import TimeState, install_timer, time_elapsing_action
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch
from simaple.spec.repository import DirectorySpecRepository


def test_archmage_fb(archmagefb_client):
    schedule = [
        ("메디테이션", "use", 0),
        ("플레임 헤이즈", "use", 0),
        ("미스트 이럽션", "use", 0),
        ("플레임 헤이즈", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 헤이즈", "use", 0),
        ("미스트 이럽션", "use", 0),
    ]

    actions = [Action(name=name, method=method) for name, method, timing in schedule]

    for action in actions:
        events = archmagefb_client.play(action)
        print(archmagefb_client.reducer.store.read_state("global.time", TimeState()))
        print([e for e in events if e.tag not in ("global.elapsed",)])


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
