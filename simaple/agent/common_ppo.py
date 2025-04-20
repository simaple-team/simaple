import os
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Callable

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
from simaple.agent.feature.environment import SimapleEnv
from simaple.agent.feature.player import SimaplePlayer
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
from simaple.agent.model.skill_network import SkillFeaturesExtractor

class MaskableActorCriticPolicy(ActorCriticPolicy):
    """
    액션 마스킹을 지원하는 Actor-Critic 정책
    """
    
    def __init__(
        self,
        observation_space: gym.spaces.Space,
        action_space: gym.spaces.Space,
        lr_schedule: Callable,
        running_penalty: float = 7.0,
        *args,
        **kwargs
    ):
        # 기본 특성 추출기 설정
        if "features_extractor_class" not in kwargs:
            kwargs["features_extractor_class"] = SkillFeaturesExtractor
        
        self.running_penalty = running_penalty

        super().__init__(
            observation_space,
            action_space,
            lr_schedule,
            *args,
            **kwargs
        )
    
    def _predict(self, observation: Dict[str, torch.Tensor], deterministic: bool = False) -> torch.Tensor:
        """
        액션 마스크를 적용하여 액션 예측
        """
        # 특성 추출 및 MLP 처리
        features = self.extract_features(observation)
        if self.share_features_extractor:
            latent_pi, latent_vf = self.mlp_extractor(features)
        else:
            pi_features, vf_features = features
            latent_pi = self.mlp_extractor.forward_actor(pi_features)
            latent_vf = self.mlp_extractor.forward_critic(vf_features)
        
        # 액션 로짓 계산
        action_logits = self.action_net(latent_pi)
        
        # 액션 마스크 적용
        if 'action_mask' in observation:
            action_mask = observation['action_mask']
            # 마스크가 0인 위치에 큰 음수값을 할당하여 선택 확률을 0에 가깝게 만듦
            action_logits = action_logits + (action_mask - 1) * 1e9

        if "running_mask" in observation:
            running_mask = observation["running_mask"]
            action_logits = action_logits - running_mask * self.running_penalty

        # 확률 분포 생성
        dist = self.action_dist.proba_distribution(action_logits)
        
        # 결정적 또는 확률적 액션 선택
        if deterministic:
            action = dist.mode()
        else:
            action = dist.sample()
        
        return action

    def forward(self, obs: Dict[str, torch.Tensor], deterministic: bool = False) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Actor-Critic 포워드 패스 (액션, 가치, 로그 확률)
        """
        features = self.extract_features(obs)
        if self.share_features_extractor:
            latent_pi, latent_vf = self.mlp_extractor(features)
        else:
            pi_features, vf_features = features
            latent_pi = self.mlp_extractor.forward_actor(pi_features)
            latent_vf = self.mlp_extractor.forward_critic(vf_features)

        values = self.value_net(latent_vf)
        action_logits = self.action_net(latent_pi)
        
        # 액션 마스크 적용
        if 'action_mask' in obs:
            action_mask = obs['action_mask']
            action_logits = action_logits + (action_mask - 1) * 1e9
        
        # 확률 분포 생성
        dist = self.action_dist.proba_distribution(action_logits)
        
        # 액션 선택
        if deterministic:
            actions = dist.mode()
        else:
            actions = dist.sample()
        
        # 로그 확률 계산
        log_probs = dist.log_prob(actions)
        
        return actions, values, log_probs
    
    def evaluate_actions(self, obs: Dict[str, torch.Tensor], actions: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        액션 평가 (가치, 로그 확률, 엔트로피)
        """
        features = self.extract_features(obs)
        if self.share_features_extractor:
            latent_pi, latent_vf = self.mlp_extractor(features)
        else:
            pi_features, vf_features = features
            latent_pi = self.mlp_extractor.forward_actor(pi_features)
            latent_vf = self.mlp_extractor.forward_critic(vf_features)
        
        action_logits = self.action_net(latent_pi)
        
        # 액션 마스크 적용
        if 'action_mask' in obs:
            action_mask = obs['action_mask']
            action_logits = action_logits + (action_mask - 1) * 1e9
        
        # 확률 분포 생성
        dist = self.action_dist.proba_distribution(action_logits)
        
        # 로그 확률 및 엔트로피 계산
        log_probs = dist.log_prob(actions)
        entropy = dist.entropy()
        
        # 가치 계산
        values = self.value_net(latent_vf)
        
        return values, log_probs, entropy


class SaveOperationsCallback(BaseCallback):
    """최고 모델의 오퍼레이션을 저장하는 콜백"""
    
    def __init__(self, eval_env: Monitor, plan_metadata_dict: dict, save_path, verbose=0):
        super(SaveOperationsCallback, self).__init__(verbose)
        self.plan_metadata_dict = plan_metadata_dict
        self.eval_env = eval_env
        self.save_path = save_path
        self.best_reward = -float("inf")
    
    def _on_step(self) -> bool:
        """정기적으로 평가 및 저장"""
        if self.n_calls % 1000 == 0:  # 1000 스텝마다 평가
            episode_reward = 0.0
            obs, _ = self.eval_env.reset()
            done = False
            
            while not done:
                action, _ = self.model.predict(obs, deterministic=True)
                obs, reward, done, _, info = self.eval_env.step(action)
                episode_reward += float(reward)
            
            if episode_reward > self.best_reward:
                self.best_reward = episode_reward
                # 오퍼레이션 저장
                operations = []
                engine = self.eval_env.env.unwrapped.player.engine
                if hasattr(engine, 'operation_logs'):
                    operations = [op for op in engine.operation_logs()]
                
                with open(os.path.join(self.save_path, "best_operations.txt"), "w") as f:
                    for op in operations:
                        if hasattr(op, 'playlogs') and op.playlogs:
                            if hasattr(op, 'command'):
                                try:
                                    f.write(f"{op.playlogs[0].clock} {op.command}\n")
                                except:
                                    f.write(f"{op.playlogs[0].clock}\n")

                with open(os.path.join(self.save_path, "best_operations.simaple"), "w") as f:
                    f.write("---\n")
                    yaml.dump(self.plan_metadata_dict, f)
                    f.write("---\n")
                    if operations:
                        for op in operations[1:]:
                            if hasattr(op, 'command'):
                                f.write(f"{op.command.command} \"{op.command.name}\"\n")

                logger.info(f"새로운 최고 보상: {self.best_reward:.2f}. 오퍼레이션 저장됨.")
            else:
                logger.info(f"현재 보상: {episode_reward:.2f}, 최고 보상: {self.best_reward:.2f}")
        return True


def setup_simulation_env(
    plan_file: str,
    target_time: int = 50_000,
    max_steps: int = 1000
) -> Tuple[SimapleEnv, Dict, SimapleEnv]:
    """시뮬레이션 환경을 설정하고 학습 및 평가용 환경을 반환"""
    # 시뮬레이션 환경 설정
    with open(plan_file, "r") as f:
        plan_metadata_dict, _ = parse_simaple_runtime(f.read())
    
    _simulation_environment_memoizer = PersistentStorageMemoizer(
        os.path.join(os.path.dirname(__file__), ".simaple.memo")
    )
    
    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)
    environment = _simulation_environment_memoizer.compute_environment(
        plan_metadata.get_environment_provider_config()  # type: ignore
    )
    
    engine = get_engine(environment)
    damage_calculator = get_damage_calculator(environment)
    player = SimaplePlayer(engine, environment.jobtype)

    # 학습용 환경 생성
    train_env = SimapleEnv(player, damage_calculator, target_time, max_steps)
    
    # 환경 검증
    check_env(train_env)
    
    # 평가용 환경 생성
    eval_player = SimaplePlayer(get_engine(environment), environment.jobtype)
    eval_env = SimapleEnv(eval_player, damage_calculator, target_time, max_steps)
    
    return train_env, plan_metadata_dict, eval_env


def evaluate_model(model, env, num_episodes=5):
    """학습된 모델 평가"""
    for episode in range(num_episodes):
        obs, _ = env.reset()
        done = False
        episode_reward = 0
        step = 0
        
        print(f"에피소드 {episode+1} 평가 시작")
        
        while not done:
            # 결정적 예측 (탐색 없음)
            action, _ = model.predict(obs, deterministic=True)
            
            # 환경에서 액션 실행
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            # 결과 업데이트
            episode_reward += reward
            step += 1
            
            print(f"Step {step}: Action={info.get('action', 'unknown')}, Reward={reward:.2f}, Total={episode_reward:.2f}, Time={info.get('time', 0):.1f}")
        
        # 에피소드 결과 출력
        print(f"에피소드 {episode+1} 완료: 총 스텝={step}, 총 보상={episode_reward:.2f}, 시간={info.get('time', 0):.1f}s\n") 