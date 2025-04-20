import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from typing import Dict, List, Tuple, Optional


class SimapleValueNetwork(nn.Module):
    """
    Simaple을 위한, 계층적 구조를 갖는 가치 네트워크
    
    입력:
    - 상태
    - 버프 액션 위치 정보
    - 데미지 액션 인덱스
    
    출력:
    - 각 액션의 정규화된 가치 확률
    """
    
    def __init__(
        self, 
        feature_dim: int,
        buff_indices: list[int],
        damage_indices: list[int],
        hidden_dim: int = 128
    ):
        """
        초기화
        
        Args:
            state_dim: 상태 벡터의 차원
            buff_dim: 버프 액션 특성의 차원
            damage_dim: 데미지 액션 특성의 차원
            n_buff_actions: 버프 액션의 수
            n_damage_actions: 데미지 액션의 수
            hidden_dim: 은닉층 차원
        """
        super(SimapleValueNetwork, self).__init__()
        

        self.action_type_net = nn.Sequential(
            nn.Linear(hidden_dim + hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 2)  # 버프 또는 데미지 선택 확률 (2개)
        )
        self.buff_indices = buff_indices
        self.damage_indices = damage_indices
    
        # 버프 액션 선택 네트워크
        self.buff_selection_net = nn.Sequential(
            nn.Linear(feature_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, len(buff_indices))
        )
        
        # 데미지 액션 선택 네트워크
        self.damage_selection_net = nn.Sequential(
            nn.Linear(feature_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, len(damage_indices))
        )
    
    def forward(
        self, 
        feature: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:

        # 액션 타입 결정 (버프 vs 데미지)
        action_type_logits = self.action_type_net(feature)
        action_type_probs = F.softmax(action_type_logits, dim=1)

        buff_logits = self.buff_selection_net(feature)
        damage_logits = self.damage_selection_net(feature)
        
        # Map using indices
        output_probs = torch.zeros(len(self.buff_indices) + len(self.damage_indices), device=feature.device)
        output_probs[self.buff_indices] = F.softmax(buff_logits, dim=1)
        output_probs[self.damage_indices] = F.softmax(damage_logits, dim=1)

        return action_type_probs, output_probs
