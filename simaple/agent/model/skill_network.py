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
                 features_dim: int = 16):

        # For type checking
        observation_space_as_typed = cast(ObservationAsTensor, observation_space)
        total_skill_count = observation_space_as_typed['skill_ids'].shape[0]
        total_features_dim = features_dim * total_skill_count + 31

        super().__init__(observation_space, total_features_dim)

        self.skill_embedding = nn.Embedding(total_skill_count, skill_embedding_dim)
        self.validity_embedding = nn.Embedding(2, validity_embedding_dim)

        self.skill_embedding_size = (
            skill_embedding_dim + validity_embedding_dim 
            + (1 * 2)  # Mask
            + (12 * 2)  # Continuous
        )

        self.skill_embedding_net = nn.Sequential(
            nn.Linear(self.skill_embedding_size, 48),
            nn.ReLU(),
            nn.Linear(48, features_dim),
            nn.ReLU(),
        )

    def forward(self, observation: ObservationAsTensor) -> torch.Tensor:
        skill_embedding = self.skill_embedding(observation['skill_ids'].to(torch.int64))
        validity_embedding = self.validity_embedding(observation['validity_discrete'].to(torch.int64))

        sequential_features = torch.cat([
            skill_embedding,
            validity_embedding,
            observation['action_mask'].unsqueeze(-1),
            observation['running_mask'].unsqueeze(-1),
            observation['running'],
            observation['validity'],
        ], dim=-1)

        encoded_features = self.skill_embedding_net(sequential_features)
        flattened_features = encoded_features.view(encoded_features.size(0), -1)

        flattened_features_with_other_features = torch.cat([
            flattened_features,
            torch.Tensor(observation['buff']),
            torch.Tensor(observation['clock']),
        ], dim=1)

        return flattened_features_with_other_features
