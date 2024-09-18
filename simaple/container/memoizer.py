import hashlib
import json
import os
from abc import ABC, abstractmethod

from simaple.container.environment_provider import (
    EnvironmentProvider,
    ProviderConfinedSimulationEnvironment,
    ProviderDependency,
    serialize_environment_provider,
)
from simaple.container.simulation import SimulationEnvironment
from simaple.core import ExtendedStat


class CharacterProviderMemo(EnvironmentProvider):
    precomputed_character: ExtendedStat
    provider_dependency: ProviderDependency

    def character(self) -> ExtendedStat:
        return self.precomputed_character

    def get_provider_dependency(
        self,
    ) -> ProviderDependency:
        return self.provider_dependency


class CharacterProviderMemoizer(ABC):
    @abstractmethod
    def get_memo(
        self,
        environment: ProviderConfinedSimulationEnvironment,
        environment_provider: EnvironmentProvider,
    ) -> tuple[EnvironmentProvider, bool]:
        pass

    def compute_environment(
        self,
        environment: ProviderConfinedSimulationEnvironment,
        environment_provider: EnvironmentProvider,
    ) -> SimulationEnvironment:
        as_environment_provider_memo, _ = self.get_memo(
            environment, environment_provider
        )

        return as_environment_provider_memo.get_simulation_environment(
            environment,
        )

    def _compute_memo_key(
        self,
        environment: ProviderConfinedSimulationEnvironment,
        environment_provider: EnvironmentProvider,
    ) -> str:
        obj = {
            "setting": environment.model_dump_json(),
            "provider": serialize_environment_provider(environment_provider),
        }
        serialized_query = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)

        hash = hashlib.sha256()
        hash.update(serialized_query.encode())
        digest = hash.hexdigest()

        return f"{environment_provider.get_name()}.{digest}"

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

    def get_memo(
        self,
        environment: ProviderConfinedSimulationEnvironment,
        environment_provider: EnvironmentProvider,
    ) -> tuple[EnvironmentProvider, bool]:
        memo_key = self._compute_memo_key(environment, environment_provider)

        if memo_key in self.memos:
            return self._deserialize_output(self.memos[memo_key]), True

        output = CharacterProviderMemo(
            precomputed_character=environment_provider.character(),
            provider_dependency=environment_provider.get_provider_dependency(),
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

    def get_memo(
        self,
        environment: ProviderConfinedSimulationEnvironment,
        environment_provider: EnvironmentProvider,
    ) -> tuple[EnvironmentProvider, bool]:
        memo_key = self._compute_memo_key(environment, environment_provider)

        with open(self.path, "r") as f:
            memos = json.load(f)

        if memo_key in memos:
            return self._deserialize_output(memos[memo_key]), True

        output = CharacterProviderMemo(
            precomputed_character=environment_provider.character(),
            provider_dependency=environment_provider.get_provider_dependency(),
        )
        memos[memo_key] = self._serialize_output(output)

        with open(self.path, "w") as f:
            json.dump(memos, f, indent=2)

        return output, False
