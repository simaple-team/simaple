from typing import Type

from fastapi.encoders import jsonable_encoder

from simaple.simulate.interface.simulator_configuration import (
    BaselineConfiguration,
    MinimalSimulatorConfiguration,
    SimulatorConfiguration,
)


class ConfigurationMapper:
    def dump(self, config: SimulatorConfiguration) -> dict:
        config_name = config.get_name()
        dumped_config = jsonable_encoder(config)
        return {
            "name": config_name,
            "dump": dumped_config,
        }

    def load(self, dumped_config: dict) -> SimulatorConfiguration:
        config_cls = self._get_configuration_cls(dumped_config["name"])
        return config_cls.model_validate(dumped_config["dump"])

    def _get_configuration_cls(self, config_name: str) -> Type[SimulatorConfiguration]:
        cls_list = [MinimalSimulatorConfiguration, BaselineConfiguration]
        cls_map: dict[str, Type[SimulatorConfiguration]] = {cls.get_name(): cls for cls in cls_list}  # type: ignore

        if config_name not in cls_map:
            raise KeyError("Configuration name not exist.")

        return cls_map[config_name]
