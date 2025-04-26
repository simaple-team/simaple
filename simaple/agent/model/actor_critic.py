import torch.nn as nn
import torch.nn.functional as F
import torch as th
from typing import Union, Tuple, Dict, List, Any, Optional
from stable_baselines3.common.utils import get_device


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
        
    def forward(self, x: th.Tensor) -> th.Tensor:
        # Multi-head self-attention with residual connection and layer normalization
        attended, _ = self.attention(x, x, x)
        x = self.norm1(x + self.dropout(attended))
        
        # Feed-forward network with residual connection and layer normalization
        x = self.norm2(x + self.dropout(self.ff(x)))
        return x


class SkillValueNetwork(nn.Module):
    """
    스킬 벡터 [batch_size, skill_count, feature_dim]를 처리하는 Transformer 기반 네트워크
    SB3 MlpExtractor 인터페이스를 준수하여 PPO와 호환되도록 함
    """
    def __init__(
        self,
        feature_dim: int,
        skill_count: int,
        embed_dim: int = 64,
        num_transformer_layers: int = 2,
        num_heads: int = 4,
        dropout: float = 0.1,
        device: Union[th.device, str] = "auto"
    ):
        super().__init__()
        self.device = get_device(device)
        self.skill_count = skill_count
        self.feature_dim = feature_dim
        self.embed_dim = embed_dim

        # Transformer 레이어
        self.transformer_layers = nn.ModuleList([
            TransformerBlock(
                embed_dim=embed_dim,
                num_heads=num_heads,
                ff_dim=embed_dim * 4,
                dropout=dropout
            ) for _ in range(num_transformer_layers)
        ])
        
        # Policy 네트워크 (Actor)
        policy_layers = []
        policy_layers.append(nn.Linear(embed_dim, 1))
        self.policy_net = nn.Sequential(*policy_layers)
        self.latent_dim_pi = skill_count
        
        # Value 네트워크 (Critic)
        value_layers = []
        value_layers.append(nn.Linear(embed_dim, 1))
        self.value_net = nn.Sequential(*value_layers)
        self.latent_dim_vf = skill_count

    def _process_features(self, features: th.Tensor) -> th.Tensor:
        """
        입력 피처를 Transformer를 통해 처리
        
        Args:
            features: [batch_size, skill_count, feature_dim] 형태의 입력 텐서
            
        Returns:
            [batch_size, skill_count, embed_dim] 형태의 처리된 피처
        """
        batch_size = features.shape[0]
        x = features
        # Transformer 레이어들 통과
        for transformer_layer in self.transformer_layers:
            x = transformer_layer(x)
            
        return x
    
    def forward(self, features: th.Tensor) -> Tuple[th.Tensor, th.Tensor]:
        """
        SB3 MlpExtractor 인터페이스 준수
        
        Args:
            features: [batch_size, skill_count, feature_dim] 형태의 입력 텐서
            
        Returns:
            (latent_policy, latent_value) 튜플
            latent_policy: [batch_size, skill_count, latent_dim_pi]
            latent_value: [batch_size, latent_dim_vf]
        """
        # Transformer를 통해 피처 처리
        transformed_features = self._process_features(features)
        
        # Policy(Actor) 네트워크 처리
        latent_policy = self.forward_actor(transformed_features)
        
        # Value(Critic) 네트워크 처리
        latent_value = self.forward_critic(transformed_features)
        
        return latent_policy, latent_value
    
    def forward_actor(self, features: th.Tensor) -> th.Tensor:
        """
        Actor 네트워크만 실행
        
        Args:
            features: [batch_size, skill_count, embed_dim] 형태의 처리된 피처
            
        Returns:
            [batch_size, skill_count, latent_dim_pi] 형태의 정책 벡터
        """
        actor_latent_vector = self.policy_net(features)
        return th.squeeze(actor_latent_vector, dim=-1)

    def forward_critic(self, features: th.Tensor) -> th.Tensor:
        """
        Critic 네트워크만 실행
        
        Args:
            features: [batch_size, skill_count, embed_dim] 형태의 처리된 피처
            
        Returns:
            [batch_size, latent_dim_vf] 형태의 가치 벡터
        """
        critic_latent_vector = self.value_net(features)
        return th.squeeze(critic_latent_vector, dim=-1)


class MlpExtractor(nn.Module):
    """
    Constructs an MLP that receives the output from a previous features extractor (i.e. a CNN) or directly
    the observations (if no features extractor is applied) as an input and outputs a latent representation
    for the policy and a value network.

    The ``net_arch`` parameter allows to specify the amount and size of the hidden layers.
    It can be in either of the following forms:
    1. ``dict(vf=[<list of layer sizes>], pi=[<list of layer sizes>])``: to specify the amount and size of the layers in the
        policy and value nets individually. If it is missing any of the keys (pi or vf),
        zero layers will be considered for that key.
    2. ``[<list of layer sizes>]``: "shortcut" in case the amount and size of the layers
        in the policy and value nets are the same. Same as ``dict(vf=int_list, pi=int_list)``
        where int_list is the same for the actor and critic.

    .. note::
        If a key is not specified or an empty list is passed ``[]``, a linear network will be used.

    :param feature_dim: Dimension of the feature vector (can be the output of a CNN)
    :param net_arch: The specification of the policy and value networks.
        See above for details on its formatting.
    :param activation_fn: The activation function to use for the networks.
    :param device: PyTorch device.
    """

    def __init__(
        self,
        feature_dim: int,
        net_arch: Union[list[int], dict[str, list[int]]],
        activation_fn: type[nn.Module],
        device: Union[th.device, str] = "auto",
    ) -> None:
        super().__init__()
        device = get_device(device)
        policy_net: list[nn.Module] = []
        value_net: list[nn.Module] = []
        last_layer_dim_pi = feature_dim
        last_layer_dim_vf = feature_dim

        # save dimensions of layers in policy and value nets
        if isinstance(net_arch, dict):
            # Note: if key is not specified, assume linear network
            pi_layers_dims = net_arch.get("pi", [])  # Layer sizes of the policy network
            vf_layers_dims = net_arch.get("vf", [])  # Layer sizes of the value network
        else:
            pi_layers_dims = vf_layers_dims = net_arch
        # Iterate through the policy layers and build the policy net
        for curr_layer_dim in pi_layers_dims:
            policy_net.append(nn.Linear(last_layer_dim_pi, curr_layer_dim))
            policy_net.append(activation_fn())
            last_layer_dim_pi = curr_layer_dim
        # Iterate through the value layers and build the value net
        for curr_layer_dim in vf_layers_dims:
            value_net.append(nn.Linear(last_layer_dim_vf, curr_layer_dim))
            value_net.append(activation_fn())
            last_layer_dim_vf = curr_layer_dim

        # Save dim, used to create the distributions
        self.latent_dim_pi = last_layer_dim_pi
        self.latent_dim_vf = last_layer_dim_vf

        # Create networks
        # If the list of layers is empty, the network will just act as an Identity module
        self.policy_net = nn.Sequential(*policy_net).to(device)
        self.value_net = nn.Sequential(*value_net).to(device)

    def forward(self, features: th.Tensor) -> tuple[th.Tensor, th.Tensor]:
        """
        :return: latent_policy, latent_value of the specified network.
            If all layers are shared, then ``latent_policy == latent_value``
        """
        return self.forward_actor(features), self.forward_critic(features)

    def forward_actor(self, features: th.Tensor) -> th.Tensor:
        return self.policy_net(features)

    def forward_critic(self, features: th.Tensor) -> th.Tensor:
        return self.value_net(features)
