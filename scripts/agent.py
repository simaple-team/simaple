import os
import time
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Union
import heapq
import copy

import fire

from simaple.container.memoizer import PersistentStorageMemoizer
from simaple.container.simulation import DamageCalculator
from simaple.container.plan_metadata import PlanMetadata
from simaple.simulate.component.view import Validity
from simaple.container.simulation import get_damage_calculator
from simaple.container.usecase.builtin import get_engine
from simaple.simulate.core.runtime import PlayLog
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.simulate.report.base import SimulationEntry
from simaple.simulate.report.feature import DamageShareFeature
from simaple.simulate.policy.base import Operation, OperationLog
from simaple.simulate.engine import OperationEngine


class Node:
    """트리 탐색에서 사용하는 노드 클래스"""
    
    def __init__(self, parent=None, action=None, engine_state=None):
        self.parent = parent
        self.action = action  # 이 노드에 도달하기 위해 수행한 액션
        self.children = []
        self.visits = 0
        self.value = 0
        self.engine_state = engine_state  # 현재 엔진 상태 (체크포인트)
        
    def add_child(self, action, engine_state):
        """자식 노드 추가"""
        child = Node(parent=self, action=action, engine_state=engine_state)
        self.children.append(child)
        return child
    
    def update(self, value):
        """노드 업데이트"""
        self.visits += 1
        self.value += value
    
    def get_uct(self, exploration_weight=1.0):
        """UCT (Upper Confidence bound applied to Trees) 값 계산"""
        if self.visits == 0 or self.parent is None or self.parent.visits == 0:
            return float('inf')
        exploitation = self.value / self.visits
        exploration = exploration_weight * np.sqrt(np.log(self.parent.visits) / self.visits)
        return exploitation + exploration


class DamageOptimizationAgent:
    """주어진 environment에서 최적의 damage를 찾아내는 Agent"""
    
    def __init__(self, engine: OperationEngine, damage_calculator, max_depth=5, max_time=10):
        self.engine = engine
        self.damage_calculator = damage_calculator
        self.max_depth = max_depth  # 최대 탐색 깊이
        self.max_time = max_time  # 최대 탐색 시간 (초)
        self.action_history = []  # 지금까지 수행한 액션 기록
        
    def get_valid_actions(self) -> List[str]:
        """현재 상태에서 유효한 액션 목록 반환"""
        viewer = self.engine.get_current_viewer()
        validity_list: list[Validity] = viewer("validity")  # validity_view는 list[Validity] 형태
        
        valid_actions = []
        for validity in validity_list:
            if validity.valid:  # Validity 객체의 valid 필드가 True인 경우
                valid_actions.append(validity.name)  # Validity 객체의 name 필드 사용
                
        return valid_actions
    
    def get_state_info(self) -> Dict[str, Any]:
        """현재 상태 정보 수집"""
        viewer = self.engine.get_current_viewer()
        
        # 각 뷰의 타입에 맞게 저장
        info_list = viewer("info")  # list[ComponentInformation]
        buff = viewer("buff")  # 합쳐진 Stat 객체
        running_list = viewer("running")  # list[Running]
        keydown_list = viewer("keydown")  # list[KeydownView]
        clock = viewer("clock")  # float
        
        # 뷰 정보 구조화
        info_dict = {info.name: info.__dict__ for info in info_list} if info_list else {}
        running_dict = {running.name: running.__dict__ for running in running_list} if running_list else {}
        keydown_dict = {kd.name: kd.__dict__ for kd in keydown_list} if keydown_list else {}
        
        return {
            "info": info_dict,
            "buff": buff,
            "running": running_dict,
            "keydown": keydown_dict,
            "clock": clock
        }
    
    def simulate_action(self, action_name: str) -> Tuple[Optional[OperationLog], float]:
        """액션 시뮬레이션 및 결과 반환"""
        operation = Operation(command="CAST", name=action_name)
        
        try:
            # 액션 실행
            operation_log = self.engine.exec(operation)
            # 데미지 계산
            total_damage = 0
            for playlog in operation_log.playlogs:
                entry = self.engine.get_simulation_entry(playlog)
                for damage_log in entry.damage_logs:
                    total_damage += self.damage_calculator.get_damage(damage_log)

            return operation_log, total_damage
        except Exception as e:
            print(f"액션 시뮬레이션 중 오류: {e}")
            return None, 0

    def rollback_to_state(self, idx: int):
        """지정한 상태로 롤백"""
        self.engine.rollback(idx)
        self.action_history = self.action_history[:idx]
    
    def beam_search(self, beam_width=3, horizon=10) -> List[str]:
        """빔 탐색을 사용하여 최적의 액션 시퀀스 찾기"""
        start_time = time.time()
        
        # 초기 상태
        current_idx = self.engine.current_index()
        best_sequence = []
        best_total_damage = 0
        
        # 빔 초기화 (점수, 상태 인덱스, 액션 시퀀스)
        beam = [(0, current_idx, [])]
        
        for step in range(horizon):
            if time.time() - start_time > self.max_time:
                print(f"시간 제한 도달: {self.max_time}초")
                break
                
            candidates = []
            
            for score, state_idx, sequence in beam:
                # 상태 복원
                self.rollback_to_state(state_idx)
                
                # 유효한 액션 가져오기
                valid_actions = self.get_valid_actions()

                for action in valid_actions:
                    # 액션 시뮬레이션
                    operation_log, damage = self.simulate_action(action)
                    if operation_log is None:
                        continue

                    # 새로운 상태 인덱스
                    new_state_idx = len(self.action_history)
                    
                    # 새로운 시퀀스 및 점수
                    new_sequence = sequence + [action]
                    new_score = score + damage
                    
                    candidates.append((new_score, new_state_idx, new_sequence))
            
            # 빔 업데이트 (상위 beam_width개 유지)
            beam = heapq.nlargest(beam_width, candidates, key=lambda x: x[0])
            
            # 최고 점수 업데이트
            if beam and beam[0][0] > best_total_damage:
                best_total_damage = beam[0][0]
                best_sequence = beam[0][2]
        
        # 최종 상태로 복원
        self.rollback_to_state(current_idx)
        
        return best_sequence
    
    def find_next_best_action(self, beam_width=3, horizon=1) -> Optional[str]:
        """다음 최적의 1개 액션만 찾기"""        
        # 현재 상태
        current_idx = self.engine.current_index()
        best_action = None
        best_damage = 0

        # 유효한 액션 가져오기
        valid_actions = self.get_valid_actions()
        
        # 각 액션 평가
        for action in valid_actions:
            # 액션 시뮬레이션
            operation_log, damage = self.simulate_action(action)
            if operation_log is None:
                continue
            
            # 롤백
            self.rollback_to_state(current_idx)
            
            # 최고 점수 업데이트
            if damage > best_damage:
                best_damage = damage
                best_action = action
        
        return best_action
    
    def mcts_search(self, iterations=100) -> Optional[str]:
        """몬테 카를로 트리 탐색을 사용하여 최적의 액션 찾기"""
        start_time = time.time()
        
        # 현재 상태 저장
        current_idx = self.engine.current_index()
        
        # 루트 노드 초기화
        root = Node(engine_state=current_idx)
        root.visits = 1
        
        for _ in range(iterations):
            if time.time() - start_time > self.max_time:
                print(f"시간 제한 도달: {self.max_time}초")
                break
                
            # 트리 정책에 따라 노드 선택 및 확장
            node = self._select_and_expand(root)
            
            # 시뮬레이션으로 보상 계산
            reward = self._simulate(node)
            
            # 백프로퍼게이션으로 결과 전파
            self._backpropagate(node, reward)
        
        # 최고의 액션 선택
        best_child = max(root.children, key=lambda child: child.value / (child.visits or 1)) if root.children else None
        best_action = best_child.action if best_child else None
        
        # 최종 상태로 복원
        self.rollback_to_state(current_idx)
        
        return best_action
    
    def _select_and_expand(self, node):
        """트리 정책: 노드 선택 및 확장"""
        # 현재 노드가 리프 노드인지 확인
        if not node.children:
            # 노드 상태로 복원
            self.rollback_to_state(node.engine_state)
            
            # 유효한 액션 가져오기
            valid_actions = self.get_valid_actions()
            
            # 각 유효한 액션에 대해 자식 노드 추가
            for action in valid_actions:
                operation_log, _ = self.simulate_action(action)
                if operation_log is not None:
                    new_state_idx = len(self.action_history)
                    node.add_child(action, new_state_idx)
            
            # 자식이 있으면 첫 번째 자식 노드 반환, 없으면 현재 노드 반환
            return node.children[0] if node.children else node
            
        # UCT를 사용하여 최적의 자식 노드 선택
        selected_child = max(node.children, key=lambda child: child.get_uct())
        
        # 선택된 자식 노드로 재귀 호출
        return self._select_and_expand(selected_child)
    
    def _simulate(self, node):
        """시뮬레이션: 무작위 정책을 사용하여 시뮬레이션 수행 및 보상 계산"""
        # 노드 상태로 복원
        self.rollback_to_state(node.engine_state)
        
        # 깊이 제한까지 무작위 액션 수행
        total_damage = 0
        simulation_depth = 0
        
        while simulation_depth < self.max_depth:
            valid_actions = self.get_valid_actions()
            if not valid_actions:
                break
                
            # 무작위 액션 선택
            action = np.random.choice(valid_actions)
            
            # 액션 시뮬레이션
            operation_log, damage = self.simulate_action(action)
            if operation_log is None:
                break
                
            total_damage += damage
            simulation_depth += 1
        
        return total_damage
    
    def _backpropagate(self, node, reward):
        """백프로퍼게이션: 노드 경로를 따라 결과 전파"""
        while node is not None:
            node.update(reward)
            node = node.parent
    
    def find_optimal_action_sequence(self, method="beam", **kwargs) -> List[str]:
        """최적의 액션 시퀀스 찾기"""
        if method == "beam":
            beam_width = kwargs.get("beam_width", 3)
            horizon = kwargs.get("horizon", 10)
            return self.beam_search(beam_width, horizon)
        elif method == "mcts":
            iterations = kwargs.get("iterations", 100)
            action = self.mcts_search(iterations)
            return [action] if action else []
        else:
            raise ValueError(f"지원하지 않는 탐색 방법: {method}")


def simulate_to_end(agent: DamageOptimizationAgent
                    , damage_calculator: DamageCalculator
                    , target_time: int = 360_000
                    , search_method: str = "beam"
                    , beam_width: int = 3
                    , horizon: int = 1
                    , iterations: int = 100) -> Tuple[List[str], int]:
    """주어진 시간까지 매 스텝마다 최적의 다음 액션을 찾아 실행"""
    executed_actions = []
    total_damage = 0
    current_time = 0
    step = 0
    
    # 무한 루프 방지를 위한 변수
    max_steps = 1000  # 최대 스텝 수 제한
    previous_time = -1
    no_progress_count = 0
    previous_actions = []  # 이전에 선택한 액션 기록
    
    print(f"시뮬레이션 시작... (목표 시간: {target_time}초)")
    
    while current_time < target_time and step < max_steps:
        step += 1
        print(f"\n스텝 {step} (현재 시간: {current_time:.1f}s)")

        # 이전 시간 기록
        previous_time = current_time
        
        # 다음 최적의 액션 찾기
        next_action = None
        if search_method == "beam":
            # 빔 서치에서는 horizon=1로 다음 1개 액션만 탐색
            next_action = agent.find_next_best_action(beam_width=beam_width, horizon=horizon)
        elif search_method == "mcts":
            next_action = agent.mcts_search(iterations=iterations)
        
        if not next_action:
            print("더 이상 유효한 액션이 없습니다.")
            break

        # 이전 액션 기록 업데이트
        previous_actions.append(next_action)
        if len(previous_actions) > 5:  # 최근 5개 액션만 기록
            previous_actions.pop(0)
            
        # 찾은 액션 실행
        print(f"선택한 액션: {next_action}")
        operation = Operation(command="CAST", name=next_action)
        operation_log = agent.engine.exec(operation)

        # 결과 계산
        action_damage = 0
        for playlog in operation_log.playlogs:
            entry = agent.engine.get_simulation_entry(playlog)
            for damage_log in entry.damage_logs:
                action_damage += damage_calculator.get_damage(damage_log)
        
        # 결과 저장
        executed_actions.append(next_action)
        total_damage += action_damage
        
        # 현재 시간 업데이트
        current_time = agent.engine.get_current_viewer()("clock")
        
        # 시간 진행 확인
        if current_time <= previous_time:
            no_progress_count += 1
            print(f"경고: 시간이 진행되지 않았습니다. ({no_progress_count}/3)")

            # 3번 연속 시간이 진행되지 않으면 중단
            if no_progress_count >= 3:
                print("오류: 시간이 3번 연속 진행되지 않아 시뮬레이션을 중단합니다.")
                break
        else:
            # 시간이 진행되면 카운터 초기화
            no_progress_count = 0
        
        # 결과 출력
        print(f"액션: {next_action}, 시간: {current_time:.1f}s, 데미지: {action_damage:,.0f}")
        
        # 중간 점검
        if step % 10 == 0:
            print(f"\n현재까지 총 데미지: {total_damage:,.0f}")
            print(f"초당 데미지: {total_damage / current_time if current_time > 0 else 0:,.0f}")
    
    # 종료 이유 출력
    if current_time >= target_time:
        print(f"\n목표 시간({target_time}초)에 도달하여 시뮬레이션을 종료합니다.")
    elif step >= max_steps:
        print(f"\n최대 스텝 수({max_steps})에 도달하여 시뮬레이션을 종료합니다.")
    
    print("\n시뮬레이션 완료")
    print(f"총 실행 스텝: {len(executed_actions)}")
    print(f"총 데미지: {total_damage:,.0f}")
    print(f"초당 데미지: {total_damage / current_time if current_time > 0 else 0:,.0f}")
    
    return executed_actions, total_damage


def run(plan_file: str, search_method="beam", max_time=10, beam_width=3, horizon=1, iterations=100, target_time=360_000):
    """매 스텝마다 최적의 다음 액션을 찾아 target_time까지 시뮬레이션 실행"""
    with open(plan_file, "r") as f:
        plan_metadata_dict, commands = parse_simaple_runtime(f.read())

    _simulation_environment_memoizer = PersistentStorageMemoizer(
        os.path.join(os.path.dirname(__file__), ".simaple.memo")
    )

    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)
    environment = _simulation_environment_memoizer.compute_environment(
        plan_metadata.get_environment_provider_config()  # type: ignore
    )

    engine = get_engine(environment)
    damage_calculator = get_damage_calculator(environment)
    
    # 유효한 액션 확인
    print("가능한 액션 목록:")
    agent: DamageOptimizationAgent = DamageOptimizationAgent(engine, damage_calculator, max_time=max_time)
    valid_actions = agent.get_valid_actions()
    for action in valid_actions:
        print(f"- {action}")
        
    if not valid_actions:
        print("사용 가능한 액션이 없습니다.")
        return
    
    # 지정된 시간까지 시뮬레이션 실행
    executed_actions, total_damage = simulate_to_end(
        agent, 
        damage_calculator, 
        target_time=target_time, 
        search_method=search_method, 
        beam_width=beam_width, 
        horizon=horizon, 
        iterations=iterations
    )
    
    # 결과 요약 출력
    print("\n실행된 액션 시퀀스:")
    for i, action in enumerate(executed_actions):
        print(f"{i+1}. {action}")
    
    current_time = agent.engine.get_current_viewer()("clock")
    print(f"\n총 데미지: {total_damage:,.0f}")
    print(f"초당 데미지: {total_damage / current_time if current_time > 0 else 0:,.0f}")
    print(f"최종 시간: {current_time:.1f}s")


def run_from_cli():
    fire.Fire(run)


if __name__ == "__main__":
    fire.Fire(run)
