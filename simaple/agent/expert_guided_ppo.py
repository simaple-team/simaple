import os
from typing import Any, Dict, List, Optional, Tuple, Union
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

from simaple.agent.buffer import TrajectoryMemory, Trajectory

# Stable Baselines 3 임포트
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv


class BehavioralCloningTrainer:
    """행동 클로닝을 통한 사전 학습 클래스"""
    
    def __init__(
        self, 
        env: SimapleEnv,
        memory: TrajectoryMemory,
        expert_actions: List[str],
        policy_kwargs: Optional[dict] = None,
        learning_rate: float = 0.0003,
    ):
        """
        행동 클로닝 학습기 초기화
        
        Args:
            env: 학습에 사용할 환경
            expert_actions: 전문가 액션 시퀀스
            policy_kwargs: 정책 네트워크 구성 인자
            learning_rate: 학습률
        """
        self.env = env
        self.expert_actions = expert_actions
        self.learning_rate = learning_rate
        self.memory = memory
        
        # 정책 초기화
        self.policy_kwargs = policy_kwargs or {
            "net_arch": [dict(pi=[128, 128], vf=[128, 128])],
            "features_extractor_class": CustomMaskableFeatureExtractor,
            "features_extractor_kwargs": dict(features_dim=128)
        }
        
        # 정책 네트워크 생성
        self.policy = MaskableActorCriticPolicy(
            self.env.observation_space,
            self.env.action_space,
            lambda _: self.learning_rate,
            **self.policy_kwargs
        )
        
        # 손실 함수와 옵티마이저 설정
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.policy.parameters(), lr=self.learning_rate)
    
    def train(self, epochs=10, batch_size=32) -> MaskableActorCriticPolicy:
        """행동 클로닝 학습 수행"""
        obs_batch, actions_batch, _, _, _ = self.memory.sample(batch_size)

        # duplicate N=20 times
        expert_states = obs_batch * 20
        expert_action_indices = actions_batch * 20

        if not expert_states:
            logger.warning("전문가 데모가 없습니다. 학습을 건너뜁니다.")
            return self.policy
        
        # 데이터셋을 배치로 분할
        n_samples = len(expert_states)
        
        logger.info(f"행동 클로닝 학습 시작 (에폭: {epochs}, 배치 크기: {batch_size}, 샘플 수: {n_samples})")
        
        for epoch in range(epochs):
            # 인덱스 셔플
            indices = np.random.permutation(n_samples)

            total_loss = 0.0
            num_batches = int(np.ceil(n_samples / batch_size))
            
            for batch_idx in tqdm(range(num_batches), desc=f"에폭 {epoch+1}/{epochs}"):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, n_samples)
                batch_indices = indices[start_idx:end_idx]
                
                # 배치 데이터 준비
                batch_states = [expert_states[i] for i in batch_indices]
                batch_actions = [expert_action_indices[i] for i in batch_indices]
                
                self.optimizer.zero_grad()
                
                # 배치 처리
                batch_losses = []
                for state, action_idx in zip(batch_states, batch_actions):
                    action_mask = torch.tensor(state["action_mask"], device=self.policy.device)
                    obs_state = torch.tensor(state["state"], device=self.policy.device)
                    
                    # 모델에서 액션 확률 분포 얻기
                    features = self.policy.extract_features({
                        "state": obs_state,
                        "action_mask": action_mask
                    })

                    # 특성 추출기 출력 처리
                    if isinstance(features, tuple):
                        # 특성 추출기가 (actor, critic) 특성을 반환하는 경우
                        actor_features = features[0]
                        latent_pi = self.policy.mlp_extractor.forward_actor(actor_features)
                    else:
                        # 특성 추출기가 공유 특성을 반환하는 경우
                        if self.policy.share_features_extractor:
                            latent_pi, _ = self.policy.mlp_extractor(features)
                        else:
                            latent_pi = self.policy.mlp_extractor.forward_actor(features)
                    
                    action_logits = self.policy.action_net(latent_pi)
                    
                    # 액션 마스크 적용 (gradient를 유지해야 하므로 detach 없이 진행)
                    action_logits = action_logits + (action_mask - 1) * 1e9
                    
                    # 손실 계산 (교차 엔트로피)
                    loss = self.criterion(
                        action_logits.unsqueeze(0),
                        torch.tensor([action_idx], device=action_logits.device)
                    )
                    batch_losses.append(loss)

                # 전체 배치 손실 계산 및 역전파
                if batch_losses:
                    batch_loss = torch.stack(batch_losses).mean()
                    batch_loss.backward()
                    self.optimizer.step()
                    total_loss += batch_loss.item()
            
            mean_loss = total_loss / num_batches if num_batches > 0 else 0
            logger.info(f"에폭 {epoch+1}/{epochs}, 평균 손실: {mean_loss:.6f}")
        
        logger.info("행동 클로닝 학습 완료")
        return self.policy


class BCCallback(BaseCallback):
    """행동 클로닝 정책과 PPO 정책의 차이를 분석하는 콜백"""
    
    def __init__(self, expert_actions: List[str], eval_env, save_path, verbose=0):
        super(BCCallback, self).__init__(verbose)
        self.expert_actions = expert_actions
        self.eval_env = eval_env
        self.save_path = save_path
    
    def _on_step(self) -> bool:
        """정기적으로 전문가 행동과 비교"""
        if self.n_calls % 5000 == 0:
            similarity = self.compare_with_expert()
            logger.info(f"스텝 {self.n_calls}: 전문가 행동과의 유사도 {similarity:.4f}")
        return True
    
    def compare_with_expert(self) -> float:
        """현재 정책과 전문가 행동 비교"""
        actions = []
        obs, _ = self.eval_env.reset()
        done = False
        
        # 현재 정책으로 에피소드 실행
        while not done:
            action, _ = self.model.predict(obs, deterministic=True)
            action_name = self.eval_env.unwrapped.all_actions[action]
            actions.append(action_name)
            obs, _, done, _, _ = self.eval_env.step(action)

        # 시퀀스 유사도 계산 (LCS 기반)
        similarity = self.sequence_similarity(actions, self.expert_actions)
        
        # 결과 저장
        with open(os.path.join(self.save_path, "expert_comparison.txt"), "a") as f:
            f.write(f"Step {self.n_calls}, 유사도: {similarity:.4f}\n")

        return similarity

    def sequence_similarity(self, seq1, seq2) -> float:
        """두 시퀀스 간의 유사도를 계산 (최장 공통 부분 수열 기준)"""
        m, n = len(seq1), len(seq2)
        if m == 0 or n == 0:
            return 0.0
        
        # 최장 공통 부분 수열(LCS) 길이 계산
        lcs = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    lcs[i][j] = lcs[i-1][j-1] + 1
                else:
                    lcs[i][j] = max(lcs[i-1][j], lcs[i][j-1])
        
        # 유사도 계산 (LCS 길이 / 두 시퀀스 길이의 최대값)
        similarity = lcs[m][n] / max(m, n)
        return similarity


def run_bc_ppo_training(
    plan_file: str,
    expert_guide_file: Optional[str] = None,
    num_timesteps=100000,
    bc_epochs=1000,
    bc_learning_rate=0.0001,
    ppo_learning_rate=0.0001,
    gamma=0.99,
    target_time=50_000,
    max_steps=200,
    log_dir="./logs/bc_ppo"
):
    """행동 클로닝으로 사전 학습된 PPO 에이전트 학습"""
    # 로그 디렉토리 생성
    os.makedirs(log_dir, exist_ok=True)
    models_dir = os.path.join(log_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # 시뮬레이션 환경 설정
    env, plan_metadata_dict, eval_env = setup_simulation_env(
        plan_file, target_time, max_steps
    )
    
    # 전문가 가이드 로드
    expert_actions = []
    if expert_guide_file and os.path.exists(expert_guide_file):
        logger.info(f"전문가 가이드 파일 로드: {expert_guide_file}")
        memory = TrajectoryMemory(expert_guide_file, env)
        # 전문가 가이드 정보 출력
        logger.info(f"전문가 액션 수: {len(expert_actions)}")
        if len(expert_actions) > 0:
            logger.info(f"첫 5개 액션: {expert_actions[:5]}")
    
    # 정책 네트워크 설정
    policy_kwargs = dict(
        net_arch=[dict(pi=[128, 128], vf=[128, 128])],
        features_extractor_class=CustomMaskableFeatureExtractor,
        features_extractor_kwargs=dict(features_dim=128)
    )
    

    # 행동 클로닝으로 사전 학습
    if expert_actions:
        logger.info("행동 클로닝(BC) 사전 학습 시작")
        bc_trainer = BehavioralCloningTrainer(
            env=env,
            memory=memory,
            expert_actions=expert_actions,
            policy_kwargs=policy_kwargs,
            learning_rate=bc_learning_rate
        )

        policy = bc_trainer.train(epochs=bc_epochs)
        
        # 사전 학습된 정책 저장
        torch.save(policy.state_dict(), os.path.join(models_dir, "bc_policy.pt"))
        logger.info(f"BC 정책 저장됨: {os.path.join(models_dir, 'bc_policy.pt')}")
    else:
        policy = None
        logger.info("전문가 가이드가 없거나 비어 있어 BC 사전 학습을 건너뜁니다.")
    
    # 환경을 Monitor로 감싸기
    env = Monitor(env, log_dir)
    eval_env = Monitor(eval_env, os.path.join(log_dir, "eval"))
    
    # 콜백 설정
    callbacks = [
        CheckpointCallback(save_freq=10000, save_path=models_dir, name_prefix="ppo_model"),
        SaveOperationsCallback(eval_env, plan_metadata_dict, log_dir)
    ]
    
    # 행동 클로닝 정책이 있으면 콜백 추가
    if expert_actions:
        callbacks.append(BCCallback(expert_actions, eval_env, log_dir))
    
    # PPO 모델 생성 (사전 학습된 정책 사용 또는 새로 생성)
    if policy:
        # 사전 학습된 정책으로 PPO 초기화
        model = PPO(
            policy=MaskableActorCriticPolicy,
            env=env,
            learning_rate=ppo_learning_rate,
            gamma=gamma,
            verbose=1,
            tensorboard_log=log_dir,
            policy_kwargs=policy_kwargs
        )
        
        # 사전 학습된 가중치 로드
        model.policy.load_state_dict(policy.state_dict())
        logger.info("사전 학습된 BC 정책으로 PPO 모델 초기화 완료")
    else:
        # 표준 PPO 모델 생성
        model = PPO(
            MaskableActorCriticPolicy,
            env,
            learning_rate=ppo_learning_rate,
            gamma=gamma,
            verbose=1,
            tensorboard_log=log_dir,
            policy_kwargs=policy_kwargs
        )
    
    # PPO 학습 실행
    print(f"PPO 학습 시작: {num_timesteps} 타임스텝, 목표 시간: {target_time}초")
    model.learn(total_timesteps=num_timesteps, callback=callbacks)
    
    # 모델 저장
    model.save(os.path.join(models_dir, "bc_ppo_final"))
    print("학습 완료 및 모델 저장됨")
    
    # 학습된 모델 평가
    print("\n학습된 모델 평가")
    evaluate_model(model, eval_env)
    
    return model


if __name__ == "__main__":
    import fire
    fire.Fire({
        "train": run_bc_ppo_training,
    }) 