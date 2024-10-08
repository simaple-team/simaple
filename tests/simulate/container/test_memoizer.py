import os
import tempfile

from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.memoizer import InMemoryMemoizer, PersistentStorageMemoizer
from simaple.core import JobType


def test_inmemory_memoizer():
    saved_memos = {}
    memoizer = InMemoryMemoizer(saved_memos)

    environment_provider = BaselineEnvironmentProvider(
        union_block_count=10,
        tier="Legendary",
        jobtype=JobType.archmagefb,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        artifact_level=40,
    )
    second_environment_provider = BaselineEnvironmentProvider(
        union_block_count=10 + 1,
        tier="Legendary",
        jobtype=JobType.archmagefb,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        artifact_level=40,
    )

    _, hit = memoizer.memoize(environment_provider)
    assert not hit

    _, hit = memoizer.memoize(environment_provider)
    assert hit

    _, hit = memoizer.memoize(second_environment_provider)
    assert not hit

    exported_memos = memoizer.export()
    new_memoizer = InMemoryMemoizer(exported_memos)
    _, hit = new_memoizer.memoize(environment_provider)
    assert hit

    _, hit = new_memoizer.memoize(second_environment_provider)
    assert hit


def test_storage_memoizer():
    with tempfile.TemporaryDirectory() as temp_dir:
        memoizer = PersistentStorageMemoizer(os.path.join(temp_dir, "memo.json"))

        environment_provider = BaselineEnvironmentProvider(
            union_block_count=10,
            tier="Legendary",
            jobtype=JobType.archmagefb,
            level=270,
            passive_skill_level=0,
            combat_orders_level=1,
            artifact_level=40,
        )
        second_environment_provider = BaselineEnvironmentProvider(
            union_block_count=10 + 1,
            tier="Legendary",
            jobtype=JobType.archmagefb,
            level=270,
            passive_skill_level=0,
            combat_orders_level=1,
            artifact_level=40,
        )

        _, hit = memoizer.memoize(environment_provider)
        assert not hit

        _, hit = memoizer.memoize(environment_provider)
        assert hit

        _, hit = memoizer.memoize(second_environment_provider)
        assert not hit

        _, hit = memoizer.memoize(environment_provider)
        assert hit

        _, hit = memoizer.memoize(second_environment_provider)
        assert hit
