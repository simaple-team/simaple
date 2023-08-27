import os

import yaml

from simaple.core import JobType, Stat
from simaple.fetch.inference.logic import JobSetting, infer_stat
from simaple.fetch.response.character import CharacterResponse


def _get_builtin_setting_file_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), "builtin", filename)


def _get_builtin_setting_file_names() -> list[str]:
    return os.listdir(os.path.join(os.path.dirname(__file__), "builtin"))


def get_from_file(filename) -> tuple[JobType, JobSetting]:
    with open(_get_builtin_setting_file_path(filename), encoding="utf-8") as f:
        raw_setting = yaml.safe_load(f)

    return JobType(raw_setting["jobtype"]), {
        "passive": Stat.parse_obj(raw_setting["passive"]),
        "candidates": [
            [Stat.parse_obj(v) if v else Stat() for v in row]
            for row in raw_setting["candidates"]
        ],
    }


_PREDEFINED_SETTING_MAP: dict[JobType, JobSetting] = {}


def _get_setting_map() -> dict[JobType, JobSetting]:
    if len(_PREDEFINED_SETTING_MAP):
        return _PREDEFINED_SETTING_MAP

    for file_name in _get_builtin_setting_file_names():
        jobtype, setting = get_from_file(file_name)
        _PREDEFINED_SETTING_MAP[jobtype] = setting

    return _PREDEFINED_SETTING_MAP


def get_predefined_setting(jobtype: JobType) -> JobSetting:
    return _get_setting_map()[jobtype]


def common_default_passive() -> Stat:
    stat = Stat()
    stat += Stat(attack_power=20, magic_attack=20)  # 여축
    stat += Stat(attack_power=5, magic_attack=5, STR=5, DEX=5, INT=5, LUK=5)  # 연합의의지
    stat += Stat(attack_power=25, magic_attack=25)  # 유니온 점령/메M
    stat += Stat(attack_power=15, magic_attack=15, STR=40, DEX=40, INT=40, LUK=40)  # 길드

    return stat


def infer_stat_by_default(
    response: CharacterResponse,
    authentic_force: int,
    size: int = -1,
):
    """
    Infer stat by default setting.
    Default setting is defined in `simaple/fetch/inference/builtin_settings.py`.
    """
    setting = get_predefined_setting(response.get_jobtype())
    return infer_stat(response, setting, authentic_force, size=size)
