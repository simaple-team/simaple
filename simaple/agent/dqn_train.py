import os
import numpy as np
import torch
import gymnasium as gym
from torch import nn

from loguru import logger

import fire

# 공통 컴포넌트 임포트
from simaple.agent.common_ppo import (
    setup_simulation_env,
    evaluate_model,
    SaveOperationsCallback
)

# Stable Baselines 3 임포트
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.noise import ActionNoise
from stable_baselines3.dqn.policies import DQNPolicy


class CustomFeatureExtractor(BaseFeaturesExtractor):
    """
    관찰 상태에서 특성을 추출하는 신경망
    """
    
    def __init__(self, observation_space: gym.spaces.Dict, features_dim: int = 128):
        # 부모 클래스 초기화
        super().__init__(observation_space, features_dim)
        
        # 상태 차원 추출 (기본값 설정)
        state_dim = 1011
        if isinstance(observation_space, gym.spaces.Dict) and 'state' in observation_space.spaces:
            state_shape = observation_space.spaces['state'].shape
            if state_shape:
                state_dim = state_shape[0]

        # 특성 추출 신경망 정의
        self.state_net = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.LayerNorm(256),
            nn.Linear(256, features_dim),
            nn.ReLU(),
        )

    def forward(self, observations):
        """
        관찰 상태에서 특성 추출
        """
        # dict 형태의 관찰인 경우
        if isinstance(observations, dict) and 'state' in observations:
            return self.state_net(observations['state'])
        
        # 텐서 형태의 관찰인 경우
        if isinstance(observations, torch.Tensor):
            return self.state_net(observations)
        
        # 예상치 못한 형태의 관찰인 경우
        device = next(self.state_net.parameters()).device
        logger.warning(f"예상치 못한 observations 유형: {type(observations)}")
        return torch.zeros((1, self.features_dim), device=device)


class MaskableDQNPolicy(DQNPolicy):
    """
    액션 마스킹이 적용된 DQN 정책
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.features_extractor = self.make_features_extractor()

    def _predict(self, observation, deterministic=False):
        """
        관찰 상태에서 액션 예측 (마스킹 적용)
        """
        with torch.no_grad():
            # 관찰 상태 처리
            obs_tensor, _ = self.obs_to_tensor(observation)
            q_values = self.q_net(obs_tensor)
            
            # 액션 마스크 적용
            if isinstance(obs_tensor, dict) and 'action_mask' in obs_tensor:
                action_mask = obs_tensor['action_mask']
                # 마스크가 0인 위치에 큰 음수값 할당
                q_values = q_values + (action_mask - 1) * 1e6

            # 최대 Q-값을 갖는 액션 선택
            actions = q_values.argmax(dim=1).cpu().numpy()
            return actions


class MaskedDQN(DQN):
    """
    액션 마스킹을 지원하는 DQN 구현
    """
    
    def __init__(
        self,
        env,
        learning_rate=1e-3,
        buffer_size=10000,
        learning_starts=1000,
        batch_size=32,
        tau=1.0,
        gamma=0.99,
        train_freq=4,
        gradient_steps=1,
        replay_buffer_class=None,
        replay_buffer_kwargs=None,
        optimize_memory_usage=False,
        target_update_interval=1000,
        exploration_fraction=0.1,
        exploration_initial_eps=1.0,
        exploration_final_eps=0.05,
        max_grad_norm=10,
        tensorboard_log=None,
        policy_kwargs=None,
        verbose=0,
        seed=None,
        device="auto",
        _init_setup_model=True,
    ):
        # 정책 설정 초기화
        policy_kwargs = policy_kwargs or {}
        if "features_extractor_class" not in policy_kwargs:
            policy_kwargs["features_extractor_class"] = CustomFeatureExtractor
        
        # 부모 클래스 초기화
        super().__init__(
            MaskableDQNPolicy,
            env,
            learning_rate=learning_rate,
            buffer_size=buffer_size,
            learning_starts=learning_starts,
            batch_size=batch_size,
            tau=tau,
            gamma=gamma,
            train_freq=train_freq,
            gradient_steps=gradient_steps,
            replay_buffer_class=replay_buffer_class,
            replay_buffer_kwargs=replay_buffer_kwargs,
            optimize_memory_usage=optimize_memory_usage,
            target_update_interval=target_update_interval,
            exploration_fraction=exploration_fraction,
            exploration_initial_eps=exploration_initial_eps,
            exploration_final_eps=exploration_final_eps,
            max_grad_norm=max_grad_norm,
            tensorboard_log=tensorboard_log,
            policy_kwargs=policy_kwargs,
            verbose=verbose,
            seed=seed,
            device=device,
            _init_setup_model=_init_setup_model,
        )
    
    def predict(self, observation, state=None, episode_start=None, deterministic=False):
        """
        액션 마스크를 고려한 액션 예측
        """
        actions = self.policy._predict(observation, deterministic=deterministic)
        return actions, state

    def _sample_action(
        self,
        learning_starts: int,
        action_noise: ActionNoise | None = None,
        n_envs: int = 1,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        액션 마스크를 고려하여 액션 샘플링
        """
        # 환경 초기화 확인
        if self._last_obs is None:
            raise ValueError("환경 초기화 실패: self._last_obs가 None입니다")

        # 현재 탐색 상태 확인
        is_warmup = self.num_timesteps < learning_starts

        # 액션 마스크 확인
        action_mask = None
        if isinstance(self._last_obs, dict) and 'action_mask' in self._last_obs:
            action_mask = self._last_obs['action_mask']

        if is_warmup:
            unscaled_action = self._sample_random_action(action_mask, n_envs)
        else:
            # 정책 기반 액션 선택
            unscaled_action, _ = self.predict(self._last_obs, deterministic=False)
            unscaled_action = self._ensure_array(unscaled_action, n_envs)
            
            # 엡실론 그리디 탐색 적용
            epsilon = self.exploration_schedule(self._current_progress_remaining)
            unscaled_action = self._apply_epsilon_greedy(
                unscaled_action, epsilon, action_mask, n_envs
            )

        # DQN은 이산 행동 공간을 사용하므로 스케일링 필요 없음
        buffer_action = unscaled_action
        
        return unscaled_action, buffer_action
    
    def _sample_random_action(self, action_mask, n_envs):
        """
        유효한 액션 중에서 무작위로 선택
        """
        if action_mask is None:
            # 마스크가 없으면 액션 공간에서 무작위 선택
            return np.array([self.action_space.sample() for _ in range(n_envs)])
        
        # 배치 차원이 있는 경우
        if len(action_mask.shape) > 1:
            actions = np.zeros(n_envs, dtype=np.int64)
            for env_idx in range(n_envs):
                valid_actions = np.where(action_mask[env_idx] > 0)[0]
                if len(valid_actions) > 0:
                    actions[env_idx] = np.random.choice(valid_actions)
                else:
                    actions[env_idx] = 0
                    logger.warning(f"환경 {env_idx}에 유효한 액션이 없습니다")
            return actions
        
        # 단일 환경 경우
        valid_actions = np.where(action_mask > 0)[0]
        if len(valid_actions) > 0:
            return np.array([np.random.choice(valid_actions)])
        else:
            logger.warning("유효한 액션이 없습니다")
            return np.array([0])
    
    def _ensure_array(self, action, n_envs):
        """
        액션이 올바른 배열 형태인지 확인
        """
        if not isinstance(action, np.ndarray) or action.shape == () or len(action.shape) == 0:
            return np.array([action] * n_envs)
        return action
    
    def _apply_epsilon_greedy(self, actions, epsilon, action_mask, n_envs):
        """
        엡실론 그리디 탐색 적용
        """
        # 엡실론 확률로 무작위 액션 선택
        if np.random.random() >= epsilon:
            return actions
            
        # 액션 마스크가 없으면 기본 엡실론 그리디 적용
        if action_mask is None:
            for env_idx in range(min(n_envs, len(actions))):
                if np.random.random() < epsilon:
                    actions[env_idx] = self.action_space.sample()
            return actions
            
        # 배치 차원이 있는 경우
        if len(action_mask.shape) > 1:
            for env_idx in range(min(n_envs, len(actions))):
                if np.random.random() < epsilon:
                    valid_actions = np.where(action_mask[env_idx] > 0)[0]
                    if len(valid_actions) > 0:
                        actions[env_idx] = np.random.choice(valid_actions)
        else:
            # 단일 환경 경우
            if np.random.random() < epsilon:
                valid_actions = np.where(action_mask > 0)[0]
                if len(valid_actions) > 0:
                    actions[0] = np.random.choice(valid_actions)
                    
        return actions


def run_dqn_training(
    plan_file: str,
    num_timesteps=100000,
    learning_rate=0.001,
    buffer_size=10000,
    learning_starts=1000,
    batch_size=32,
    tau=1.0,
    gamma=0.99,
    train_freq=4,
    target_update_interval=1000,
    exploration_fraction=0.1,
    exploration_initial_eps=1.0,
    exploration_final_eps=0.05,
    target_time=50_000,
    max_steps=200,
    log_dir="./logs/dqn"
):
    """DQN 알고리즘으로 에이전트 학습"""
    # 로그 디렉토리 생성
    os.makedirs(log_dir, exist_ok=True)
    models_dir = os.path.join(log_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # 시뮬레이션 환경 설정
    env, plan_metadata_dict, eval_env = setup_simulation_env(
        plan_file, target_time, max_steps
    )

    # 환경을 Monitor로 감싸기
    monitor_env = Monitor(env, log_dir)
    eval_env = Monitor(eval_env, os.path.join(log_dir, "eval"))
    
    # 콜백 설정
    callbacks = [
        CheckpointCallback(save_freq=10000, save_path=models_dir, name_prefix="dqn_model"),
        SaveOperationsCallback(eval_env, plan_metadata_dict, log_dir),
    ]
    
    # 정책 설정
    policy_kwargs = dict(
        features_extractor_class=CustomFeatureExtractor,
        features_extractor_kwargs=dict(features_dim=128),
        net_arch=[256, 256]
    )

    # 마스킹 지원 DQN 모델 생성
    model = MaskedDQN(
        monitor_env,
        learning_rate=learning_rate,
        buffer_size=buffer_size,
        learning_starts=learning_starts,
        batch_size=batch_size,
        tau=tau,
        gamma=gamma,
        train_freq=train_freq,
        target_update_interval=target_update_interval,
        exploration_fraction=exploration_fraction,
        exploration_initial_eps=exploration_initial_eps,
        exploration_final_eps=exploration_final_eps,
        verbose=1,
        tensorboard_log=log_dir,
        policy_kwargs=policy_kwargs
    )
    
    # 학습 실행
    logger.info(f"DQN 학습 시작: {num_timesteps} 타임스텝, 목표 시간: {target_time}초")
    model.learn(total_timesteps=num_timesteps, callback=callbacks)
    
    # 모델 저장
    model_path = os.path.join(models_dir, "dqn_final")
    model.save(model_path)
    logger.info(f"학습 완료 및 모델 저장됨: {model_path}")
    
    # 학습된 모델 평가
    logger.info("학습된 모델 평가 시작")
    evaluate_model(model, eval_env)
    
    return model


def run_dqn_evaluation(
    plan_file: str, 
    model_path="./logs/dqn/models/dqn_final.zip", 
    target_time=50_000, 
    max_steps=1000
):
    """저장된 DQN 모델로 평가만 수행"""
    # 시뮬레이션 환경 설정
    env, _, _ = setup_simulation_env(plan_file, target_time, max_steps)
    
    # 모델 로드
    if os.path.exists(model_path):
        model = MaskedDQN.load(model_path)
        logger.info(f"모델 로드됨: {model_path}")
    else:
        logger.error(f"모델 파일을 찾을 수 없음: {model_path}")
        return
    
    # 평가 실행
    logger.info(f"평가 시작: 목표 시간: {target_time}초")
    evaluate_model(model, env)


if __name__ == "__main__":
    fire.Fire({
        "train": run_dqn_training,
        "evaluate": run_dqn_evaluation
    }) 