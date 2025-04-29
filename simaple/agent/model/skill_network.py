from typing import cast
import torch
import gymnasium as gym
from torch import nn
import torch

from simaple.agent.feature.encoder import ObservationAsTensor
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor



class TransformerBlock(nn.Module):
    """
    트랜스포머 블록 구현: Multi-head self-attention + Feed Forward Network
    """
    def __init__(
        self, 
        embed_dim: int, 
        num_heads: int = 4, 
        ff_dim: int = 64, 
        dropout: float = 0.1
    ):
        super().__init__()
        self.attention = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout, batch_first=True)
        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.ff = nn.Sequential(
            nn.Linear(embed_dim, ff_dim),
            nn.ReLU(),
            nn.Linear(ff_dim, embed_dim),
            nn.Dropout(dropout)
        )
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Multi-head self-attention with residual connection and layer normalization
        attended, _ = self.attention(x, x, x)
        x = self.norm1(x + self.dropout(attended))
        
        # Feed-forward network with residual connection and layer normalization
        x = self.norm2(x + self.dropout(self.ff(x)))
        return x


class SkillFeaturesExtractor(BaseFeaturesExtractor):
    """
    액션 마스킹을 지원하는 특성 추출기
    """
    
    def __init__(self, observation_space: gym.spaces.Dict, 
                 skill_embedding_dim: int = 32,
                 validity_embedding_dim: int = 8,
                 features_dim: int = 16,
                 final_features_dim: int = 2,
                 running_mask_embedding_dim: int = 8,
                 action_mask_embedding_dim: int = 8,
                 cooldown_zero_embedding_dim: int = 8):

        # For type checking
        observation_space_as_typed = cast(ObservationAsTensor, observation_space)
        total_skill_count = observation_space_as_typed['skill_ids'].shape[0]
        total_features_dim = (final_features_dim) * (total_skill_count + 2)

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
            + 4 # Clock
        )

        self.skill_embedding_net = nn.Sequential(
            nn.Linear(self.skill_embedding_size, 64),
            nn.ReLU(),
            nn.Linear(64, features_dim),
            nn.ReLU(),
        )
        
        self.total_skill_count = total_skill_count
        self.buff_embedding_network = nn.Sequential(
            nn.Linear(27, features_dim),
            nn.GELU(),
            nn.Linear(features_dim, features_dim),
        )

        self.clock_embedding_network = nn.Sequential(
            nn.Linear(4, features_dim),
            nn.GELU(),
            nn.Linear(features_dim, features_dim),
        )

        self.transformer_layers = nn.ModuleList([
            TransformerBlock(features_dim, num_heads=4, dropout=0.0, ff_dim=32) for _ in range(1)
        ])

        self.feature_to_latent = nn.Sequential(
            nn.Linear(features_dim, features_dim // 2),
            nn.ReLU(),
            nn.Linear(features_dim // 2, final_features_dim)
        )

    def forward(self, observation: ObservationAsTensor) -> torch.Tensor:
        batch_size = observation['skill_ids'].size(0)
        skill_embedding = self.skill_embedding(observation['skill_ids'].to(torch.int64))
        validity_embedding = self.validity_embedding(observation['validity_discrete'].to(torch.int64))
        running_mask_embedding = self.running_mask_embedding(observation['running_mask'].to(torch.int64))
        action_mask_embedding = self.action_mask_embedding(observation['action_mask'].to(torch.int64))
        cooldown_zero_embedding = self.cooldown_zero_embedding(observation['cooldown_zero'].to(torch.int64))

        repeated_clock_embedding = observation['clock'].unsqueeze(1).repeat(1, self.total_skill_count, 1)

        sequential_features = torch.cat([
            skill_embedding,
            validity_embedding,
            running_mask_embedding,
            action_mask_embedding,
            cooldown_zero_embedding,
            observation['running'],
            observation['validity'],
            repeated_clock_embedding,
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

        for layer in self.transformer_layers:
            skill_features_with_globals = layer(skill_features_with_globals)

        latent_features = self.feature_to_latent(skill_features_with_globals)
        return latent_features.reshape(batch_size, -1)
