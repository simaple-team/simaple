import hashlib
import json
import os
from abc import ABC, abstractmethod

from simaple.container.character_provider import (
    deserialize_character_provider,
    serialize_character_provider,
)
from simaple.container.simulation import (
    CharacterDependentSimulationConfig,
    CharacterProvidingConfig,
    SimulationContainer,
    SimulationSetting,
)
from simaple.core import ExtendedStat, JobType


class CachedCharacterProvider(CharacterProvidingConfig):
    cached_character: ExtendedStat
    cached_simulation_config: CharacterDependentSimulationConfig

    def character(self) -> ExtendedStat:
        return self.cached_character

    def get_character_dependent_simulation_config(
        self,
    ) -> CharacterDependentSimulationConfig:
        return self.cached_simulation_config


class CharacterProviderCache(ABC):
    @abstractmethod
    def get(
        self, setting: SimulationSetting, character_provider: CharacterProvidingConfig
    ) -> tuple[CharacterProvidingConfig, bool]:
        pass

    def get_simulation_container(
        self, setting: SimulationSetting, character_provider: CharacterProvidingConfig
    ) -> SimulationContainer:
        as_cached_character_provider, _ = self.get(setting, character_provider)

        return SimulationContainer(setting, as_cached_character_provider)

    def _compute_cache_key(
        self, setting: SimulationSetting, character_provider: CharacterProvidingConfig
    ) -> str:
        obj = {
            "setting": setting.model_dump_json(),
            "provider": serialize_character_provider(character_provider),
        }
        serialized_query = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)

        hash = hashlib.sha256()
        hash.update(serialized_query.encode())
        digest = hash.hexdigest()

        return f"{character_provider.__class__.__name__}.{digest}"

    def _deserialize_output(self, value: str) -> CachedCharacterProvider:
        cached_provider = CachedCharacterProvider.model_validate_json(value)

        return cached_provider

    def _serialize_output(self, value: CachedCharacterProvider) -> str:
        return value.model_dump_json(indent=2)


class InMemoryCache(CharacterProviderCache):
    def __init__(self, saved_cache: dict[str, str] | None = None) -> None:
        if saved_cache is None:
            saved_cache = {}

        self.cache = saved_cache

    def get(
        self, setting: SimulationSetting, character_provider: CharacterProvidingConfig
    ) -> tuple[CharacterProvidingConfig, bool]:
        cache_key = self._compute_cache_key(setting, character_provider)

        if cache_key in self.cache:
            return self._deserialize_output(self.cache[cache_key]), True

        output = CachedCharacterProvider(
            cached_character=character_provider.character(),
            cached_simulation_config=character_provider.get_character_dependent_simulation_config(),
        )
        self.cache[cache_key] = self._serialize_output(output)
        return output, False

    def export(self) -> dict[str, str]:
        return self.cache


class PersistentStorageCache(CharacterProviderCache):
    def __init__(self, path: str = ".simaple.cache") -> None:
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({}, f)

    def get(
        self, setting: SimulationSetting, character_provider: CharacterProvidingConfig
    ) -> tuple[CharacterProvidingConfig, bool]:
        cache_key = self._compute_cache_key(setting, character_provider)

        with open(self.path, "r") as f:
            cache = json.load(f)

        if cache_key in cache:
            return self._deserialize_output(cache[cache_key]), True

        output = CachedCharacterProvider(
            cached_character=character_provider.character(),
            cached_simulation_config=character_provider.get_character_dependent_simulation_config(),
        )
        cache[cache_key] = self._serialize_output(output)

        with open(self.path, "w") as f:
            json.dump(cache, f, indent=2)

        return output, False
