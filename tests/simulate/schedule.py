from simaple.simulate.base import Action


def get_archmagefb_schedule() -> list[Action]:
    schedule = [
        ("플레임 헤이즈", "use", 0),
        ("미스트 이럽션", "use", 800),
        ("플레임 헤이즈", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 스윕", "use", 0),
        ("플레임 헤이즈", "use", 0),
        ("미스트 이럽션", "use", 800),
    ]

    return [Action(name=name, method=method) for name, method, timing in schedule]
