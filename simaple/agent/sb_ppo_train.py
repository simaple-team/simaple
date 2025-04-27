import os

import fire
import numpy as np

from simaple.agent.common_ppo import (
    MaskableActorCriticPolicy,
    SaveOperationsCallback,
    setup_simulation_env,
    evaluate_model
)
from simaple.agent.model.skill_network import SkillFeaturesExtractor
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import EvalCallback

def linear_schedule(initial_value: float, final_value: float = 0.0):
    """
    선형 학습률 스케줄러
    :param initial_value: 초기 학습률
    :param final_value: 최종 학습률
    :return: 현재 진행 상황에 따른 학습률을 반환하는 함수
    """
    def func(progress_remaining: float) -> float:
        """
        progress_remaining: 1.0부터 시작하여 0.0으로 감소
        """
        return final_value + progress_remaining * (initial_value - final_value)
    return func


def cosine_schedule(initial_value: float, final_value: float = 0.0):
    """
    코사인 학습률 스케줄러
    :param initial_value: 초기 학습률
    :param final_value: 최종 학습률
    :return: 현재 진행 상황에 따른 학습률을 반환하는 함수
    """
    def func(progress_remaining: float) -> float:
        """
        progress_remaining: 1.0부터 시작하여 0.0으로 감소
        """
        cosine_decay = 0.5 * (1 + np.cos(np.pi * (1 - progress_remaining)))
        return final_value + cosine_decay * (initial_value - final_value)
    return func


def warmup_cosine_schedule(initial_value: float, final_value: float = 0.0, warmup_fraction: float = 0.1):
    """
    웜업이 포함된 코사인 학습률 스케줄러
    :param initial_value: 최대 학습률 (웜업 후 도달할 값)
    :param final_value: 최종 학습률
    :param warmup_fraction: 총 학습 중 웜업에 사용할 비율 (0.0~1.0)
    :return: 현재 진행 상황에 따른 학습률을 반환하는 함수
    """
    def func(progress_remaining: float) -> float:
        """
        progress_remaining: 1.0부터 시작하여 0.0으로 감소
        """
        progress_done = 1.0 - progress_remaining
        
        # 웜업 단계 (시작 학습률은 initial_value의 1/10)
        if progress_done < warmup_fraction:
            # 웜업 중: 학습률을 initial_value의 1/10에서 initial_value까지 선형적으로 증가
            warmup_progress = progress_done / warmup_fraction
            return initial_value * (0.1 + 0.9 * warmup_progress)
        
        # 웜업 이후 코사인 감소
        cosine_progress = (progress_done - warmup_fraction) / (1.0 - warmup_fraction)
        cosine_decay = 0.5 * (1 + np.cos(np.pi * cosine_progress))
        return final_value + cosine_decay * (initial_value - final_value)
    
    return func


def warmup_linear_schedule(initial_value: float, final_value: float = 0.0, warmup_fraction: float = 0.1):
    """
    웜업이 포함된 선형 학습률 스케줄러
    :param initial_value: 최대 학습률 (웜업 후 도달할 값)
    :param final_value: 최종 학습률
    :param warmup_fraction: 총 학습 중 웜업에 사용할 비율 (0.0~1.0)
    :return: 현재 진행 상황에 따른 학습률을 반환하는 함수
    """
    def func(progress_remaining: float) -> float:
        """
        progress_remaining: 1.0부터 시작하여 0.0으로 감소
        """
        progress_done = 1.0 - progress_remaining
        
        # 웜업 단계 (시작 학습률은 initial_value의 1/10)
        if progress_done < warmup_fraction:
            # 웜업 중: 학습률을 initial_value의 1/10에서 initial_value까지 선형적으로 증가
            warmup_progress = progress_done / warmup_fraction
            return initial_value * (0.1 + 0.9 * warmup_progress)
        
        # 웜업 이후 선형 감소
        linear_progress = (progress_done - warmup_fraction) / (1.0 - warmup_fraction)
        return initial_value - linear_progress * (initial_value - final_value)
    
    return func


def run_training_sb3(
    plan_file: str,
    num_timesteps=100000,
    learning_rate=0.00003,
    final_learning_rate=0.00003,
    lr_schedule_type="linear",
    warmup_fraction=0.05,
    gamma=0.99,
    target_time=50_000,
    max_steps=200,
    log_dir="./logs"
):
    """Stable Baselines 3의 PPO 알고리즘으로 에이전트 학습"""
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

    # 평가 콜백 설정 (학습 중 주기적으로 평가 및 로깅)
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=os.path.join(models_dir, "best_model"),
        log_path=log_dir,
        eval_freq=5000,
        deterministic=True,
        render=False,
        verbose=1,
    )

    # 콜백 설정
    callbacks = [
        CheckpointCallback(save_freq=10000, save_path=models_dir, name_prefix="ppo_model"),
        SaveOperationsCallback(eval_env, plan_metadata_dict, log_dir),
        eval_callback
    ]
    
    # 학습률 스케줄러 설정
    if lr_schedule_type == "linear":
        lr_schedule = linear_schedule(learning_rate, final_learning_rate)
    elif lr_schedule_type == "cosine":
        lr_schedule = cosine_schedule(learning_rate, final_learning_rate)
    elif lr_schedule_type == "warmup_cosine":
        lr_schedule = warmup_cosine_schedule(learning_rate, final_learning_rate, warmup_fraction)
    elif lr_schedule_type == "warmup_linear":
        lr_schedule = warmup_linear_schedule(learning_rate, final_learning_rate, warmup_fraction)
    else:  # constant
        lr_schedule = learning_rate
    
    # 모델 생성
    policy_kwargs = dict(
        features_extractor_class=SkillFeaturesExtractor,
        features_extractor_kwargs=dict(
            skill_embedding_dim=32,
            validity_embedding_dim=8,
            features_dim=8,
        ),
        running_penalty=2.1,
        net_arch=[] # type: ignore
    )

    model = PPO(
        MaskableActorCriticPolicy,
        monitor_env,
        learning_rate=lr_schedule,
        gamma=gamma,
        stats_window_size=3000,
        batch_size=64,
        n_epochs=32,
        verbose=1,
        ent_coef=0.3,
        tensorboard_log=log_dir,
        policy_kwargs=policy_kwargs
    )
    
    # 학습 실행
    print(f"학습 시작: {num_timesteps} 타임스텝, 목표 시간: {target_time}초")
    if lr_schedule_type.startswith("warmup_"):
        print(f"학습률 스케줄러: {lr_schedule_type}, 초기값: {learning_rate}, 최종값: {final_learning_rate}, 웜업 비율: {warmup_fraction}")
    elif lr_schedule_type != "constant":
        print(f"학습률 스케줄러: {lr_schedule_type}, 초기값: {learning_rate}, 최종값: {final_learning_rate}")
    else:
        print(f"학습률: 고정값 {learning_rate}")
    
    model.learn(total_timesteps=num_timesteps, callback=callbacks)
    
    # 모델 저장
    model.save(os.path.join(models_dir, "ppo_final"))
    print("학습 완료 및 모델 저장됨")
    
    # 학습된 모델 평가
    print("\n학습된 모델 평가")
    evaluate_model(model, eval_env)
    
    return model


def run_evaluation_sb3(plan_file: str, model_path="./logs/models/ppo_final.zip", target_time=50_000, max_steps=1000):
    """저장된 SB3 PPO 모델로 평가만 수행"""
    # 시뮬레이션 환경 설정
    env, _, _ = setup_simulation_env(plan_file, target_time, max_steps)
    
    # 모델 로드
    if os.path.exists(model_path):
        model = PPO.load(model_path, policy=MaskableActorCriticPolicy)  # 커스텀 정책 지정
        print(f"모델 로드됨: {model_path}")
    else:
        print(f"모델 파일을 찾을 수 없음: {model_path}")
        return
    
    # 평가 실행
    print(f"평가 시작: 목표 시간: {target_time}초")
    evaluate_model(model, env)


if __name__ == "__main__":
    fire.Fire({
        "train": run_training_sb3,
        "evaluate": run_evaluation_sb3
    })
