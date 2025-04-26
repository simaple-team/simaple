import os
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Callable, cast

import numpy as np
import torch
import gymnasium as gym
from gymnasium import spaces
from torch import nn
import torch
import yaml

from loguru import logger
from simaple.agent.feature.encoder import ObservationAsTensor
# Stable Baselines 3 임포트
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common import utils
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor


class SkillFeaturesExtractor(BaseFeaturesExtractor):
    """
    액션 마스킹을 지원하는 특성 추출기
    """
    
    def __init__(self, observation_space: gym.spaces.Dict, 
                 skill_embedding_dim: int = 32,
                 validity_embedding_dim: int = 8,
                 features_dim: int = 16,
                 running_mask_embedding_dim: int = 8,
                 action_mask_embedding_dim: int = 8,
                 cooldown_zero_embedding_dim: int = 8):

        # For type checking
        observation_space_as_typed = cast(ObservationAsTensor, observation_space)
        total_skill_count = observation_space_as_typed['skill_ids'].shape[0]
        total_features_dim = features_dim

        super().__init__(observation_space, total_features_dim)

        self.skill_embedding = nn.Embedding(total_skill_count, skill_embedding_dim)
        self.validity_embedding = nn.Embedding(2, validity_embedding_dim)

        self.running_mask_embedding = nn.Embedding(2, running_mask_embedding_dim)
        self.action_mask_embedding = nn.Embedding(2, action_mask_embedding_dim)
        self.cooldown_zero_embedding = nn.Embedding(2, cooldown_zero_embedding_dim)

        self.skill_embedding_size = (
            skill_embedding_dim + validity_embedding_dim 
            + running_mask_embedding_dim + action_mask_embedding_dim + cooldown_zero_embedding_dim
            + (12 * 2)  # Continuous
        )

        self.skill_embedding_net = nn.Sequential(
            nn.Linear(self.skill_embedding_size, 64),
            nn.ReLU(),
            nn.Linear(64, features_dim),
            nn.ReLU(),
        )
        
        self.total_skill_count = total_skill_count
        self.buff_embedding_network = nn.Sequential(
            nn.Linear(27, 64),
            nn.ReLU(),
            nn.Linear(64, features_dim),
            nn.ReLU(),
        )
        
        self.clock_embedding_network = nn.Sequential(
            nn.Linear(4, 64),
            nn.ReLU(),
            nn.Linear(64, features_dim),
            nn.ReLU(),
        )

    def forward(self, observation: ObservationAsTensor) -> torch.Tensor:
        batch_size = observation['skill_ids'].size(0)
        skill_embedding = self.skill_embedding(observation['skill_ids'].to(torch.int64))
        validity_embedding = self.validity_embedding(observation['validity_discrete'].to(torch.int64))
        running_mask_embedding = self.running_mask_embedding(observation['running_mask'].to(torch.int64))
        action_mask_embedding = self.action_mask_embedding(observation['action_mask'].to(torch.int64))
        cooldown_zero_embedding = self.cooldown_zero_embedding(observation['cooldown_zero'].to(torch.int64))

        sequential_features = torch.cat([
            skill_embedding,
            validity_embedding,
            running_mask_embedding,
            action_mask_embedding,
            cooldown_zero_embedding,
            observation['running'],
            observation['validity'],
        ], dim=-1)

        encoded_features = self.skill_embedding_net(sequential_features)
        # 이제 평탄화하지 않고 [batch_size, skill_count, features_dim] 형태 유지
        
        # buff와 clock 피처를 각 스킬에 브로드캐스팅
        buff = torch.Tensor(observation['buff'])
        clock = torch.Tensor(observation['clock'])
        
        buff_expanded = self.buff_embedding_network(buff)
        clock_expanded = self.clock_embedding_network(clock)

        buff_expanded = buff_expanded.unsqueeze(1)
        clock_expanded = clock_expanded.unsqueeze(1)

        # [batch_size, skill_count + 2, features_dim] 형태로 합치기
        skill_features_with_globals = torch.cat([
            encoded_features,
            buff_expanded,
            clock_expanded
        ], dim=1)
        
        return skill_features_with_globals
