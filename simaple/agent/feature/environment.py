import os
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Callable, cast

import numpy as np
import torch
import gymnasium as gym
from gymnasium import spaces
from torch import nn
import yaml

from simaple.container.memoizer import PersistentStorageMemoizer
from simaple.container.plan_metadata import PlanMetadata
from simaple.container.simulation import get_damage_calculator, DamageCalculator
from simaple.container.usecase.builtin import get_engine
from simaple.simulate.policy.base import Operation, OperationLog
from simaple.simulate.policy.parser import parse_simaple_runtime

from simaple.agent.feature.player import SimaplePlayer
from simaple.agent.feature.encoder import encode_state_info
from loguru import logger

# Stable Baselines 3 임포트
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common import utils
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor




class SimapleEnv(gym.Env):
    """Stable Baselines 3용 심플 환경 클래스"""
    def __init__(self, 
                 player: SimaplePlayer, 
                 damage_calculator: DamageCalculator, 
                 target_time=50_000,
                 max_steps=1000):
        super(SimapleEnv, self).__init__()
        
        self.player = player
        self.damage_calculator = damage_calculator
        self.target_time = target_time
        self.max_steps = max_steps

        self.current_step = 0
        self.current_time = 0
        self.total_reward = 0

        self.all_actions = self.player.get_all_actions()
        logger.info(self.all_actions)

        # 액션 및 관찰 공간 정의
        n_actions = len(self.all_actions)
        self.action_space = spaces.Discrete(n_actions)

        # 상태 차원 확인
        sampled_state = encode_state_info(self.all_actions, self.player.get_state_info())

        def float_as_space(tensor: np.ndarray) -> spaces.Space:
            return spaces.Box(low=-np.inf, high=np.inf, shape=tensor.shape, dtype=np.float32)

        def int_as_space(tensor: np.ndarray) -> spaces.Space:
            return spaces.Box(low=0, high=1, shape=tensor.shape, dtype=np.int64)

        self.observation_space = spaces.Dict({
            "buff": float_as_space(sampled_state["buff"]),
            "running": float_as_space(sampled_state["running"]),
            "validity": float_as_space(sampled_state["validity"]),
            "validity_discrete": int_as_space(sampled_state["validity_discrete"]),
            "action_mask": int_as_space(sampled_state["action_mask"]),
            "running_mask": int_as_space(sampled_state["running_mask"]),
            "cooldown_zero": int_as_space(sampled_state["cooldown_zero"]),
            "skill_ids": spaces.Box(low=0, high=n_actions, shape=sampled_state["skill_ids"].shape, dtype=np.int64),
            "clock": float_as_space(sampled_state["clock"]),
        })
        logger.info(self.observation_space)
    
    def reset(self, seed=None):
        """환경 초기화"""
        self.player.engine.rollback(0)
        self.current_step = 0
        self.current_time = 0
        self.total_reward = 0
        
        # 초기 상태 정보 및 유효한 액션
        state_info = self.player.get_state_info()
        valid_actions = self.player.get_valid_actions()
        
        # 상태 및 액션 마스크 인코딩
        state_tensor = encode_state_info(self.all_actions, state_info)
        
        # Dict 형태의 관찰 상태 반환
        return state_tensor, {
            'step': self.current_step,
            'time': (self.target_time - self.current_time),
            'valid_actions': valid_actions
        }

    def step(self, action_idx):
        """액션 실행 단계"""
        action_name = self.all_actions[action_idx]
        valid_actions = self.player.get_valid_actions()
        
        done = False
        info = {}
        
        # 유효하지 않은 액션 처리
        if action_name not in valid_actions:
            logger.warning(f"선택된 액션이 유효하지 않음: {action_name}")
            # 페널티 부여
            reward = -5.0
            next_state_info = self.player.get_state_info()
        else:
            # 액션 실행
            operation_log, reward = self.simulate_action(action_name)
            
            if operation_log is None:
                logger.warning(f"액션 실행 실패: {action_name}")
                reward = -0.1
                next_state_info = self.player.get_state_info()
            else:
                # 다음 상태 정보
                next_state_info = self.player.get_state_info()
                self.current_time = next_state_info.get("clock", 0)
                
                # 종료 여부 확인
                done = self.current_time >= self.target_time or self.current_step >= self.max_steps
        
        # 상태 업데이트
        self.current_step += 1
        self.total_reward += reward
        
        # 새로운 상태 및 액션 마스크 인코딩
        new_valid_actions = self.player.get_valid_actions()
        observation = encode_state_info(self.all_actions, next_state_info)
        
        # 정보 업데이트
        info = {
            'step': self.current_step,
            'time': (self.target_time - self.current_time),
            'action': action_name,
            'valid_actions': new_valid_actions,
            'total_reward': self.total_reward
        }
        
        return observation, reward, done, done, info
    
    def simulate_action(self, action_name: str) -> Tuple[Optional[OperationLog], float]:
        """액션 시뮬레이션 및 결과 반환"""
        operation = Operation(command="CAST", name=action_name)
        damage_normalizer = 1_0000_0000_0000  # 1조
        step_penalty = 0.0
        
        try:
            # 액션 실행
            operation_log = self.player.engine.exec(operation)
            
            # 데미지 계산
            total_damage = 0
            for playlog in operation_log.playlogs:
                entry = self.player.engine.get_simulation_entry(playlog)
                for damage_log in entry.damage_logs:
                    total_damage += self.damage_calculator.get_damage(damage_log)
            
            return operation_log, total_damage / damage_normalizer - step_penalty
        
        except Exception as e:
            logger.error(f"액션 시뮬레이션 중 오류: {e}")
            return None, 0

    def get_running_mask(self) -> torch.Tensor:
        """실행 중인 스킬 마스크 반환"""
        running = self.player.get_state_info()["running"]
        mask = torch.zeros(len(self.all_actions))
        for name, running_info in running.items():
            if running_info.lasting_duration and running_info.name in self.all_actions:
                mask[self.all_actions.index(name)] = 1

        return mask

    def render(self, mode='human'):
        """환경 렌더링 (선택적)"""
        if mode == 'human':
            logger.info(f"Step: {self.current_step}, Time: {self.current_time:.1f}, Reward: {self.total_reward:.2f}")
        return None
