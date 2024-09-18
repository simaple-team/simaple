import hashlib
import json
import os
from abc import ABC, abstractmethod

from simaple.container.environment_provider import (
    MemoizableEnvironment,
    MemoizableEnvironmentProvider,
)
from simaple.container.simulation import SimulationEnvironment


def _serialize_environment_provider(provider: MemoizableEnvironmentProvider) -> str:
    obj = {
        "config": provider.model_dump_json(),
        "config_name": provider.get_name(),
    }

    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


class CharacterProviderMemo(MemoizableEnvironmentProvider):
    provider_dependency: MemoizableEnvironment

    def get_memoizable_environment(
        self,
    ) -> MemoizableEnvironment:
        return self.provider_dependency


class CharacterProviderMemoizer(ABC):
    @abstractmethod
    def memoize(
        self,
        memoizable_environment_provider: MemoizableEnvironmentProvider,
    ) -> tuple[MemoizableEnvironmentProvider, bool]:
        """
        Memoize the environment provider and return the memoized environment provider if it exists.
        If not memoized, memoize into storage and return the memoized environment provider.
        """
        pass

    def compute_environment(
        self,
        memoizable_environment_provider: MemoizableEnvironmentProvider,
    ) -> SimulationEnvironment:
        as_environment_provider_memo, _ = self.memoize(memoizable_environment_provider)

        return as_environment_provider_memo.get_simulation_environment()

    def _compute_memo_key(
        self,
        memoizable_environment_provider: MemoizableEnvironmentProvider,
    ) -> str:
        obj = {
            "setting": memoizable_environment_provider.independent_environment.model_dump_json(),
            "provider": _serialize_environment_provider(
                memoizable_environment_provider
            ),
        }
        serialized_query = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)

        hash = hashlib.sha256()
        hash.update(serialized_query.encode())
        digest = hash.hexdigest()

        return f"{memoizable_environment_provider.get_name()}.{digest}"

    def _deserialize_output(self, value: str) -> CharacterProviderMemo:
        provider_memo = CharacterProviderMemo.model_validate_json(value)

        return provider_memo

    def _serialize_output(self, value: CharacterProviderMemo) -> str:
        return value.model_dump_json(indent=2)


class InMemoryMemoizer(CharacterProviderMemoizer):
    def __init__(self, saved_memos: dict[str, str] | None = None) -> None:
        if saved_memos is None:
            saved_memos = {}

        self.memos = saved_memos

    def memoize(
        self,
        memoizable_environment_provider: MemoizableEnvironmentProvider,
    ) -> tuple[MemoizableEnvironmentProvider, bool]:
        memo_key = self._compute_memo_key(memoizable_environment_provider)

        if memo_key in self.memos:
            return self._deserialize_output(self.memos[memo_key]), True

        output = CharacterProviderMemo(
            provider_dependency=memoizable_environment_provider.get_memoizable_environment(),
            independent_environment=memoizable_environment_provider.independent_environment,
        )
        self.memos[memo_key] = self._serialize_output(output)
        return output, False

    def export(self) -> dict[str, str]:
        return self.memos


class PersistentStorageMemoizer(CharacterProviderMemoizer):
    def __init__(self, path: str = ".simaple.memo") -> None:
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({}, f)

    def memoize(
        self,
        memoizable_environment_provider: MemoizableEnvironmentProvider,
    ) -> tuple[MemoizableEnvironmentProvider, bool]:
        memo_key = self._compute_memo_key(memoizable_environment_provider)

        with open(self.path, "r") as f:
            memos = json.load(f)

        if memo_key in memos:
            return self._deserialize_output(memos[memo_key]), True

        output = CharacterProviderMemo(
            provider_dependency=memoizable_environment_provider.get_memoizable_environment(),
            independent_environment=memoizable_environment_provider.independent_environment,
        )
        memos[memo_key] = self._serialize_output(output)

        with open(self.path, "w") as f:
            json.dump(memos, f, indent=2)

        return output, False
