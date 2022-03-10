from pydantic import BaseModel
from typing import Optional, List, Tuple, Dict, Union
from simaple.core.base import Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType
from simaple.gear.blueprint import PracticalGearBlueprint
from simaple.gear.gear_repository import GearRepository
from simaple.benchmark.gearset_blueprint import UserGearsetBlueprint

import yaml
import json
import enum
import os


INTERPETER_RESOURCE_PATH = os.path.join(
    os.path.dirname(__file__), "resources"
)

class BenchmarkInterpreterOption(BaseModel):
    stat_priority: Tuple[str, str, str, str]
    attack_priority: Tuple[str, str]
    job_index: int

    class Macro:
        first_stat = 'first_stat'
        second_stat = 'second_stat'
        third_stat = 'third_stat'
        fourth_stat  = 'fourth_stat'

        first_att = 'first_att'
        second_att = 'second_att'

        all_stat = 'all_stat'
        all_att = 'all_att'

    def translate(self, maybe_representation: Union[int, str, float]) -> str:
        if not isinstance(maybe_representation, str):
            return maybe_representation

        interpreted_key = maybe_representation
        interpreted_key = interpreted_key.replace(self.Macro.first_stat, self.stat_priority[0])
        interpreted_key = interpreted_key.replace(self.Macro.second_stat, self.stat_priority[1])
        interpreted_key = interpreted_key.replace(self.Macro.third_stat, self.stat_priority[2])
        interpreted_key = interpreted_key.replace(self.Macro.fourth_stat, self.stat_priority[3])

        interpreted_key = interpreted_key.replace(self.Macro.first_att, self.attack_priority[0])
        interpreted_key = interpreted_key.replace(self.Macro.second_att, self.attack_priority[1])

        return interpreted_key

    def translate_all_stat(self, k, v):
        assert self.Macro.all_stat in k
        unraveled = {}
        for stat in [
            self.Macro.first_stat,
            self.Macro.second_stat,
            self.Macro.third_stat,
            self.Macro.fourth_stat,
        ]:
            unraveled[self.translate(k.replace(
                self.Macro.all_stat,
                stat
            ))] = self.translate(v)
        
        return unraveled

    def translate_all_att(self, k, v):
        assert self.Macro.all_att in k
        unraveled = {}
        for att in [
            self.Macro.first_att,
            self.Macro.second_att,
        ]:
            unraveled[self.translate(k.replace(
                self.Macro.all_att,
                att
            ))] = self.translate(v)

        return unraveled

class BenchmarkConfigurationInterpreter:
    def __init__(self):
        self.item_name_alias = self.load_interpreter_data(os.path.join(INTERPETER_RESOURCE_PATH, 'item_name_alias.json'))

    def load_interpreter_data(self, v: Optional[Union[Dict, str]]):
        if v is None:
            return {}
        if isinstance(v, str):
            with open(v, encoding='utf-8') as f:
                return json.load(f)
        if isinstance(v, dict):
            return v
    
        raise TypeError()

    def interpret_gear_id(self, name: str, job_index: int) -> str:
        if name in self.item_name_alias:
            return self.item_name_alias[name][job_index]
        
        return name

    def _interpret(self, raw: Union[List, Dict], opt: BenchmarkInterpreterOption):
        if isinstance(raw, list):
            return [
                self._interpret(arg, opt) for arg in raw
            ]

        if isinstance(raw, int) or isinstance(raw, float) or isinstance(raw, str):
            return opt.translate(raw)

        interpreted = {}

        excluded_keys = raw.get('exclude', []) + ['exclude']
        for k, v in raw.items():
            if k in excluded_keys:
                continue
            if isinstance(v, dict) or isinstance(v, list):
                interpreted[k] = self._interpret(v, opt)
            else:
                if k == 'gear_id':
                    interpreted['gear_id'] = self.interpret_gear_id(v, opt.job_index)
                elif BenchmarkInterpreterOption.Macro.all_stat in k:
                    interpreted.update(opt.translate_all_stat(k, v))
                elif BenchmarkInterpreterOption.Macro.all_att in k:
                    interpreted.update(opt.translate_all_att(k, v))
                else:
                    interpreted[opt.translate(k)] = opt.translate(v)

        return interpreted

    def interpret_user_gearset_from_file(self, file_path, opt):
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_configuration = yaml.safe_load(f)
        
        return self.interpret_user_gearset(raw_configuration, opt)

    def interpret_user_gearset(self, raw_configuration, opt):
        interpreted_configuration = self._interpret(raw_configuration['default'], opt)
        return UserGearsetBlueprint.parse_obj(interpreted_configuration)
