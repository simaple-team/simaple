import os

from typing import Any  

import torch

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
    keydown: dict[str, KeydownView]
    clock: float


class StateEncoder(ABC):
    @abstractmethod
    def encode_state(self, state_info: StateInfo) -> torch.Tensor:
        ...

    @abstractmethod
    def encode_action_mask(self, valid_actions: list[str]) -> torch.Tensor:
        ...


class BaselineStateEncoder(StateEncoder):
    def __init__(self, actions: list[str], initial_state_for_build: StateInfo):
        self.actions = actions
        self.initial_state_for_build = initial_state_for_build
        
        self._action_map: dict[str, int] = {action: idx for idx, action in enumerate(actions)}

        self._running_names: list[str] = sorted(
            [name for name in initial_state_for_build["running"].keys()]
        )
        self._keydown_names: list[str] = sorted(
            [name for name in initial_state_for_build["keydown"].keys()]
        )
        self._info_names: list[str] = sorted([name for name in initial_state_for_build["info"].keys()])

    def encode_state(self, state_info: StateInfo) -> torch.Tensor:
        return torch.cat([
            encode_buff_as_tensor(state_info["buff"]),
            encode_running_as_tensor(state_info["running"]),
            encode_keydown_as_tensor(state_info["keydown"]),
            encode_info_as_tensor(state_info["info"]),
        ])

    def encode_action_mask(self, valid_actions: list[str]) -> torch.Tensor:
        mask = torch.zeros(len(self.actions))

        for action in valid_actions:
            action_idx = self._action_map.get(action)
            if action_idx is not None:
                mask[action_idx] = 1

        return mask


class SimaplePlayer:
    def __init__(self, engine: OperationEngine):
        self.engine = engine

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

        return all_actions

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
        clock: float = viewer("clock")
        info_dict: dict[str, ComponentInformation] = {
            info.name: info
            for info in viewer("info")
        }

        return StateInfo(
            info=info_dict, 
            buff=buff,
            running=running_dict,
            keydown=keydown_dict,
            clock=clock,
        )
