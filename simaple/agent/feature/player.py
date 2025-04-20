import os

from typing import Any  

import torch
import yaml
from simaple.core.jobtype import JobType
import fire
from simaple.simulate.component.base import Stat
import numpy as np
from simaple.simulate.component.view import Accessiblity, Validity
from simaple.simulate.engine import OperationEngine
from simaple.simulate.policy.base import Operation, OperationLog
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.simulate.component.base import ComponentInformation, Accessiblity
from simaple.simulate.component.view import Validity, Running, KeydownView

from simaple.agent.encoder import encode_buff_as_tensor, encode_running_as_tensor, encode_keydown_as_tensor, encode_info_as_tensor

from abc import ABC, abstractmethod
from typing import TypedDict


class StateInfo(TypedDict):
    info: dict[str, ComponentInformation]
    buff: Stat | None
    running: dict[str, Running]
    validity: dict[str, Validity]
    keydown: dict[str, KeydownView]
    clock: float


class SkillPriority(TypedDict):
    buff_skill_priority: list[str]
    damage_skill_priority: list[str]
    name: str


def get_skill_priority(job_name: str) -> SkillPriority:
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "hint", f"{job_name}.yaml"), "r") as f:
        return yaml.safe_load(f)


class SimaplePlayer:
    def __init__(self, engine: OperationEngine, job: JobType):
        self.engine = engine
        self.skill_priority = get_skill_priority(job.value)

    def get_all_actions(self) -> list[str]:
        """사용 가능한 모든 액션 목록 반환"""
        viewer = self.engine.get_current_viewer()
        validity_list: list[Validity] = viewer("validity")
        accessiblity_list: list[Accessiblity] = viewer("accessiblity")
        accessible_names = [
            accessiblity.name
            for accessiblity in accessiblity_list
            if not accessiblity.hidden
        ]

        all_actions = []
        for validity in validity_list:
            if validity.name in accessible_names:
                all_actions.append(validity.name)

        return sorted(all_actions)

    def get_buff_skills(self) -> list[str]:
        """버프 스킬 목록 반환"""
        return self.skill_priority["buff_skill_priority"]

    def get_damage_skills(self) -> list[str]:
        """데미지 스킬 목록 반환"""
        return self.skill_priority["damage_skill_priority"]

    def get_valid_actions(self) -> list[str]:
        """현재 상태에서 유효한 액션 목록 반환"""
        viewer = self.engine.get_current_viewer()
        validity_list: list[Validity] = viewer("validity")
        accessiblity_list: list[Accessiblity] = viewer("accessiblity")
        accessiblity_names = [
            accessiblity.name
            for accessiblity in accessiblity_list
            if not accessiblity.hidden
        ]

        valid_actions = []
        for validity in validity_list:
            if validity.valid and validity.name in accessiblity_names:
                valid_actions.append(validity.name)

        return valid_actions

    def get_state_info(self) -> StateInfo:
        """현재 상태 정보 수집"""
        viewer = self.engine.get_current_viewer()

        # 각 뷰의 타입에 맞게 저장
        buff: Stat | None = viewer("buff")
        running_dict: dict[str, Running] = {
            running.name: running
            for running in viewer("running")
        }
        keydown_dict: dict[str, KeydownView] = {
            kd.name: kd
            for kd in viewer("keydown")
        }
        validity_dict: dict[str, Validity] = {
            v.name: v
            for v in viewer("validity")
        }
        clock: float = viewer("clock")
        info_dict: dict[str, ComponentInformation] = {
            info.name: info
            for info in viewer("info")
        }

        return StateInfo(
            info=info_dict, 
            buff=buff,
            running=running_dict,
            validity=validity_dict,
            keydown=keydown_dict,
            clock=clock,
        )
