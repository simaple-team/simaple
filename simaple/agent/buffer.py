import os
from typing import TypedDict
import numpy as np
import torch
import gymnasium as gym
from torch import nn
import yaml
from tqdm import tqdm

from simaple.container.memoizer import PersistentStorageMemoizer
from simaple.container.plan_metadata import PlanMetadata
from simaple.container.simulation import get_damage_calculator, DamageCalculator
from simaple.container.usecase.builtin import get_engine
from simaple.simulate.policy.base import Operation, OperationLog
from simaple.simulate.policy.parser import parse_simaple_runtime

from simaple.agent.player import BaselineStateEncoder, SimaplePlayer
from simaple.agent.sb_ppo_train import (
    MaskableActorCriticPolicy,
    CustomMaskableFeatureExtractor, 
    SaveOperationsCallback
)
from loguru import logger

# 공통 컴포넌트 임포트
from simaple.agent.common_ppo import (
    setup_simulation_env,
    evaluate_model,
    SimapleEnv,
)


def load_actions_from_file(file_path: str) -> list[str]:
    """파일에서 액션 시퀀스 로드"""
    with open(file_path, "r") as f:
        _, operations = parse_simaple_runtime(f.read())
    
    actions = []
    for operation in operations:
        if operation.command_type == "operation":
            actions.append(operation.name)

    return actions  


class Trajectory(TypedDict):
    state: dict
    action: int
    reward: float
    next_state: dict
    done: bool


def compile_expert_trajectory(actions: list[str], env: SimapleEnv) -> list[Trajectory]:
    trajectory: list[Trajectory] = []

    obs, _ = env.reset()
    
    for action_name in actions:
        if action_name in env.all_actions:
            previous_obs = obs
            action_idx = env.all_actions.index(action_name)
            obs, reward, done, _, info = env.step(action_idx)
            trajectory.append({
                "state": previous_obs,
                "action": action_idx,
                "reward": reward,
                "next_state": obs,
                "done": done
            })

            if done:
                break

    return trajectory


class TrajectoryMemory:    
    def __init__(self, expert_guide_file: str, env: SimapleEnv):

        self.expert_actions = load_actions_from_file(expert_guide_file)
        self.env = env

        trajectory = compile_expert_trajectory(self.expert_actions, self.env)

        self.buffer: list[Trajectory] = trajectory


    def sample(self, batch_size: int) -> list[tuple[
        dict[str, np.ndarray],
        np.ndarray,
        np.ndarray,
        dict[str, np.ndarray],
        np.ndarray
    ]]:
        """버퍼에서 무작위로 경험 샘플링"""
        indices = np.random.randint(0, len(self.buffer), size=batch_size)
        batch = [self.buffer[i] for i in indices]

        # 배치 데이터 분리 및 텐서 변환
        obs, actions, rewards, next_obs, dones = zip(*batch)
        
        # 각 컴포넌트를 적절한 형태로 변환
        obs_batch = {
            'state': np.stack([o['state'] for o in obs]),
            'action_mask': np.stack([o['action_mask'] for o in obs])
        }
        actions_batch = np.array(actions)
        rewards_batch = np.array(rewards)
        next_obs_batch = {
            'state': np.stack([no['state'] for no in next_obs]),
            'action_mask': np.stack([no['action_mask'] for no in next_obs])
        }
        dones_batch = np.array(dones)
        
        return obs_batch, actions_batch, rewards_batch, next_obs_batch, dones_batch
    
    def __len__(self):
        return len(self.buffer)
