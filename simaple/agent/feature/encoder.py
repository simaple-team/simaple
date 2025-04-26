from typing import TypedDict

from simaple.simulate.component.base import Stat
from simaple.simulate.component.view import (
    Running,
    Validity,
)
import torch

import numpy as np
from simaple.agent.feature.player import StateInfo

def power_expansion(x: float) -> list[float]:
    return [
        x ** 0.5, x, x ** 2, x ** 3
    ]

_ordered_stat_keys = list(Stat.__annotations__.keys())
_empty_stat = Stat()


def encode_stat_as_tensor(stat: Stat) -> np.ndarray:
    stat_values = [getattr(stat, key) / 100 for key in _ordered_stat_keys]
    return np.array(stat_values, dtype=np.float32)


def encode_running(running: Running | None) -> np.ndarray:
    if running is None:
        return np.zeros([12], dtype=np.float32)

    absolute_time_left = min(max(running.time_left / 1000, 0), 600)
    absolute_lasting_duration = min(max(running.lasting_duration / 1000, 0), 600)

    relative_time_left = min(max(absolute_time_left / (absolute_lasting_duration + 0.000001), 0), 1)

    return np.array([
        *power_expansion(relative_time_left),
        *power_expansion(absolute_time_left),
        *power_expansion(absolute_lasting_duration),
    ], dtype=np.float32)
    

def encode_validity_discrete(validity: Validity | None) -> np.ndarray:
    if validity is None:
        return np.zeros([1], dtype=np.int64)

    return np.array([
        1 if validity.valid else 0,
    ], dtype=np.int64)

def encode_validity_continuous(validity: Validity | None) -> np.ndarray:
    if validity is None:
        return np.zeros([12], dtype=np.float32)

    absolute_cooldown_duration = min(max(validity.cooldown_duration / 1000, 0), 600)
    absolute_time_left = min(max(validity.time_left / 1000, 0), 600)
    relative_cooldown_duration = min(max(absolute_time_left / (absolute_cooldown_duration + 0.000001), 0), 1)

    return np.array([
        *power_expansion(relative_cooldown_duration),
        *power_expansion(absolute_cooldown_duration),
        *power_expansion(absolute_time_left),
    ], dtype=np.float32)


def encode_clock(clock: float) -> np.ndarray:
    return np.array([
        *power_expansion(clock / 1000),
    ], dtype=np.float32)


class Observation(TypedDict):
    buff: np.ndarray
    running: np.ndarray
    validity: np.ndarray
    validity_discrete: np.ndarray
    action_mask: np.ndarray
    running_mask: np.ndarray
    skill_ids: np.ndarray
    clock: np.ndarray
    cooldown_zero: np.ndarray


class ObservationAsTensor(TypedDict):
    buff: torch.Tensor
    running: torch.Tensor
    validity: torch.Tensor
    validity_discrete: torch.Tensor
    action_mask: torch.Tensor
    running_mask: torch.Tensor
    skill_ids: torch.Tensor
    clock: torch.Tensor
    common_feature: torch.Tensor
    cooldown_zero: torch.Tensor


def encode_state_info(skill_names: list[str], state_info: StateInfo) -> Observation:
    running_tensors = []
    validity_tensors = []
    validity_discrete_tensors = []
    action_mask = []
    running_mask = []
    skill_ids = []
    cooldown_zero = []

    buff = state_info["buff"]
    if buff is None:
        buff = _empty_stat

    for idx, name in enumerate(skill_names):
        running = state_info["running"].get(name)
        validity = state_info["validity"].get(name)
        info = state_info["info"].get(name)
        assert info is not None

        action_masked = (
            float(validity is not None and validity.valid)
        )
        running_masked = (
            float(running is not None and running.time_left > 0)
        )

        running_tensors.append(encode_running(running))
        validity_tensors.append(encode_validity_continuous(validity))
        cooldown_zero.append(info.props["cooldown_duration"] == 0)
        validity_discrete_tensors.append(encode_validity_discrete(validity))
        action_mask.append(action_masked)
        running_mask.append(running_masked)
        skill_ids.append(idx)    

    return {
        "buff": encode_stat_as_tensor(buff),
        "running": np.array(running_tensors, dtype=np.float32),
        "validity": np.array(validity_tensors, dtype=np.float32),
        "validity_discrete": np.concatenate(validity_discrete_tensors, dtype=np.int64),
        "cooldown_zero": np.array(cooldown_zero, dtype=np.int32),
        "action_mask": np.array(action_mask, dtype=np.int32),
        "running_mask": np.array(running_mask, dtype=np.int32),
        "skill_ids": np.array(skill_ids, dtype=np.int64),
        "clock": encode_clock(state_info["clock"]),
    }

