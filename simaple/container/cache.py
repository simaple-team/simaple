import hashlib
import json
from abc import ABC, abstractmethod

from simaple.container.character_provider import (
    deserialize_character_provider,
    serialize_character_provider,
)
from simaple.container.simulation import (
    CharacterDependentSimulationConfig,
    CharacterProvidingConfig,
    SimulationSetting,
)
from simaple.core import ExtendedStat, JobType


class LocalstorageCache:
    def __init__(self, saved_cache: dict[str, str] | None = None) -> None:
        if saved_cache is None:
            saved_cache = {}

        self.cache = saved_cache

    def get(
        self, setting: SimulationSetting, character_provider: CharacterProvidingConfig
    ) -> tuple[tuple[ExtendedStat, CharacterDependentSimulationConfig], bool]:
        cache_key = self._compute_cache_key(setting, character_provider)

        if cache_key in self.cache:
            return self._deserialize_output(self.cache[cache_key]), True

        output = (
            character_provider.character(),
            character_provider.get_character_dependent_simulation_config(),
        )
        self.cache[cache_key] = self._serialize_output(output)
        return output, False

    def export(self) -> dict[str, str]:
        return self.cache

    def _deserialize_output(
        self, value: str
    ) -> tuple[ExtendedStat, CharacterDependentSimulationConfig]:
        deserialized_value = json.loads(value)

        return (
            ExtendedStat.model_validate_json(deserialized_value["stat"]),
            CharacterDependentSimulationConfig.model_validate_json(
                deserialized_value["config"]
            ),
        )

    def _serialize_output(
        self, value: tuple[ExtendedStat, CharacterDependentSimulationConfig]
    ) -> str:
        return json.dumps(
            {
                "stat": value[0].model_dump_json(),
                "config": value[1].model_dump_json(),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

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
