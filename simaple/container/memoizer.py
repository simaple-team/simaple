import hashlib
import json
import os
from abc import ABC, abstractmethod
from typing import Any

from simaple.container.environment_provider import (
    EnvironmentProvider,
    MemoizableEnvironmentProvider,
)
from simaple.container.simulation import SimulationEnvironment


class CharacterProviderMemo(EnvironmentProvider):
    memoizable_environment: dict[str, Any]
    independent_environment: dict[str, Any]

    def get_memoizable_environment(
        self,
    ) -> dict[str, Any]:
        return self.memoizable_environment

    def get_memoization_independent_environment(
        self,
    ) -> dict[str, Any]:
        return self.independent_environment

    def get_simulation_environment(self) -> SimulationEnvironment:
        environment_dict = self.get_memoization_independent_environment()
        environment_dict.update(self.get_memoizable_environment())

        environment = SimulationEnvironment.model_validate(environment_dict)
        return environment


class CharacterProviderMemoizer(ABC):
    @abstractmethod
    def memoize(
        self,
        memoizable_environment_provider: MemoizableEnvironmentProvider,
    ) -> tuple[EnvironmentProvider, bool]:
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
            "setting": memoizable_environment_provider.get_memoization_key(),
            "name": memoizable_environment_provider.get_name(),
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
    ) -> tuple[EnvironmentProvider, bool]:
        memo_key = self._compute_memo_key(memoizable_environment_provider)

        if memo_key in self.memos:
            memoized_environment_provider = self._deserialize_output(self.memos[memo_key])
            return (
                CharacterProviderMemo(
                    memoizable_environment=memoized_environment_provider.memoizable_environment,  # memoized
                    independent_environment=memoizable_environment_provider.get_memoization_independent_environment(),  # not memoized
                ),
                True,
            )

        output = CharacterProviderMemo(
            memoizable_environment=memoizable_environment_provider.get_memoizable_environment(),
            independent_environment=memoizable_environment_provider.get_memoization_independent_environment(),
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
    ) -> tuple[EnvironmentProvider, bool]:
        memo_key = self._compute_memo_key(memoizable_environment_provider)

        with open(self.path, "r") as f:
            memos = json.load(f)

        if memo_key in memos:
            memoized_environment_provider = self._deserialize_output(memos[memo_key])
            return (
                CharacterProviderMemo(
                    memoizable_environment=memoized_environment_provider.memoizable_environment,  # memoized
                    independent_environment=memoizable_environment_provider.get_memoization_independent_environment(),  # not memoized
                ),
                True,
            )

        output = CharacterProviderMemo(
            memoizable_environment=memoizable_environment_provider.get_memoizable_environment(),
            independent_environment=memoizable_environment_provider.get_memoization_independent_environment(),
        )
        memos[memo_key] = self._serialize_output(output)

        with open(self.path, "w") as f:
            json.dump(memos, f, indent=2)

        return output, False
