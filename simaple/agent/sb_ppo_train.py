import os

import fire

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


def run_training_sb3(
    plan_file: str,
    num_timesteps=100000,
    learning_rate=0.001,
    gamma=0.99,
    target_time=25_000,
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
    
    # 콜백 설정
    callbacks = [
        CheckpointCallback(save_freq=10000, save_path=models_dir, name_prefix="ppo_model"),
        SaveOperationsCallback(eval_env, plan_metadata_dict, log_dir)
    ]
    
    # 모델 생성
    policy_kwargs = dict(
        net_arch=[dict(pi=[128, 128], vf=[128, 128])],
        features_extractor_class=SkillFeaturesExtractor,
        features_extractor_kwargs=dict(
            skill_embedding_dim=64,
            validity_embedding_dim=8,
            features_dim=32
        ),
        running_penalty=2.1
    )

    model = PPO(
        MaskableActorCriticPolicy,
        monitor_env,
        learning_rate=learning_rate,
        gamma=gamma,
        stats_window_size=1000,
        batch_size=256,
        n_epochs=40,
        verbose=1,
        tensorboard_log=log_dir,
        policy_kwargs=policy_kwargs
    )
    
    # 학습 실행
    print(f"학습 시작: {num_timesteps} 타임스텝, 목표 시간: {target_time}초")
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
