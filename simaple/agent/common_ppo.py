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

from simaple.agent.player import BaselineStateEncoder, SimaplePlayer
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


class CustomMaskableFeatureExtractor(BaseFeaturesExtractor):
    """
    액션 마스킹을 지원하는 특성 추출기
    """
    
    def __init__(self, observation_space: gym.spaces.Dict, features_dim: int = 128):
        # 부모 클래스에는 전체 observation_space를 넘기지만, 실제로는 state만 처리
        super().__init__(observation_space, features_dim)
        
        # 상태 차원 추출
        state_dim = observation_space.spaces['state'].shape[0]
        
        # 특성 추출 네트워크 정의
        self.state_net = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, features_dim),
            nn.ReLU(),
        )

    def forward(self, observations: Dict[str, torch.Tensor]) -> torch.Tensor:
        # state 특성만 추출
        state_features = self.state_net(observations['state'])
        return state_features


class MaskableActorCriticPolicy(ActorCriticPolicy):
    """
    액션 마스킹을 지원하는 Actor-Critic 정책
    """
    
    def __init__(
        self,
        observation_space: gym.spaces.Space,
        action_space: gym.spaces.Space,
        lr_schedule: Callable,
        logit_bias: list[float] | None = None,
        running_penalty: float = 7.0,
        *args,
        **kwargs
    ):
        # 기본 특성 추출기 설정
        if "features_extractor_class" not in kwargs:
            kwargs["features_extractor_class"] = CustomMaskableFeatureExtractor
        
        self.logit_bias = torch.tensor(logit_bias, dtype=torch.float32)
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

        if self.logit_bias is not None:
            action_logits = action_logits + self.logit_bias

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


class SimapleEnv(gym.Env):
    """Stable Baselines 3용 심플 환경 클래스"""
    def __init__(self, player: SimaplePlayer, damage_calculator: DamageCalculator, target_time=50_000, max_steps=1000):
        super(SimapleEnv, self).__init__()
        
        self.player = player
        self.damage_calculator = damage_calculator
        self.target_time = target_time
        self.max_steps = max_steps
        
        self.current_step = 0
        self.current_time = 0
        self.total_reward = 0
        
        # 상태 인코더 초기화
        self.state_encoder = BaselineStateEncoder(
            self.player.get_all_actions(), 
            self.player.get_state_info()
        )

        # 액션 및 관찰 공간 정의
        n_actions = len(self.player.get_all_actions())
        self.action_space = spaces.Discrete(n_actions)
        
        # 상태 차원 확인
        state_dim = self.state_encoder.encode_state(self.player.get_state_info()).shape[0]
        logger.info(f"State dimension: {state_dim}")
        self.observation_space = spaces.Dict({
            'state': spaces.Box(low=-np.inf, high=np.inf, shape=(state_dim,), dtype=np.float32),
            'action_mask': spaces.Box(low=0, high=1, shape=(n_actions,), dtype=np.float32),
            "running_mask": spaces.Box(low=0, high=1, shape=(n_actions,), dtype=np.float32)
        })

        # 액션 목록 저장
        self.all_actions = self.player.get_all_actions()
    
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
        state_tensor = self.state_encoder.encode_state(state_info)
        action_mask = self.state_encoder.encode_action_mask(valid_actions)
        
        # Dict 형태의 관찰 상태 반환
        return {
            'state': state_tensor.numpy(),
            'action_mask': action_mask.numpy(),
            "running_mask": self.get_running_mask().numpy()
        }, {
            'step': self.current_step,
            'time': self.current_time,
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
            reward = -0.1
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
        next_state_tensor = self.state_encoder.encode_state(next_state_info)
        next_action_mask = self.state_encoder.encode_action_mask(new_valid_actions)
        
        # 정보 업데이트
        info = {
            'step': self.current_step,
            'time': self.current_time,
            'action': action_name,
            'valid_actions': new_valid_actions,
            'total_reward': self.total_reward
        }
        
        # Dict 형태의 관찰 상태 반환
        observation = {
            'state': next_state_tensor.numpy(),
            'action_mask': next_action_mask.numpy(),
            "running_mask": self.get_running_mask().numpy()
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