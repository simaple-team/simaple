import os

import yaml

from simaple.core import JobType, Stat
from simaple.fetch.inference.logic import JobSetting


def _get_builtin_setting_file_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), "builtin", filename)


def get_from_file(filename) -> JobSetting:
    with open(_get_builtin_setting_file_path(filename), encoding="utf-8") as f:
        raw_setting = yaml.safe_load(f)

    return {
        "passive": Stat.parse_obj(raw_setting["passive"]),
        "candidates": [[
            Stat.parse_obj(v) if v else Stat() for v in row
        ] for row in raw_setting["candidates"]],
    }


_PREDEFINED_SETTING_MAP: dict[JobType, JobSetting] = {
    JobType.archmagefb: get_from_file("archmagefp.yaml"),
    JobType.bishop: get_from_file("bishop.yaml"),
    JobType.illium: get_from_file("illium.yaml"),
    JobType.luminous: get_from_file("luminous.yaml"),
}


def get_predefined_setting(jobtype: JobType) -> JobSetting:
    return _PREDEFINED_SETTING_MAP[jobtype]


def common_default_passive() -> Stat:
    stat = Stat()
    stat += Stat(attack_power=20, magic_attack=20)  # 여축
    stat += Stat(attack_power=5, magic_attack=5, STR=5, DEX=5, INT=5, LUK=5)  # 연합의의지
    stat += Stat(attack_power=25, magic_attack=25)  # 유니온 점령/메M
    stat += Stat(attack_power=15, magic_attack=15, STR=40, DEX=40, INT=40, LUK=40)  # 길드

    return stat
