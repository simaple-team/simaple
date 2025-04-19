from simaple.simulate.component.base import Stat
from simaple.simulate.component.view import Running, KeydownView, ComponentInformation
import torch


_ordered_stat_keys = list(Stat.__annotations__.keys())
_empty_stat = Stat()


def encode_stat_as_tensor(stat: Stat) -> torch.Tensor:
    """
    Stat 객체를 PyTorch 텐서로 변환합니다.
    
    Args:
        stat (Stat): 변환할 Stat 객체
        
    Returns:
        torch.Tensor: Stat 객체의 모든 속성값을 포함하는 1차원 텐서
    """
    # Stat 객체의 모든 속성값을 리스트로 변환
    stat_values = [getattr(stat, key) / 100 for key in _ordered_stat_keys]
    
    # 리스트를 PyTorch 텐서로 변환
    return torch.tensor(stat_values, dtype=torch.float32)


def encode_buff_as_tensor(buff: Stat | None) -> torch.Tensor:
    """
    버프 딕셔너리를 PyTorch 텐서로 변환합니다.
    
    Args:
        buff (dict[str, Stat | None]): 버프 이름을 키로, Stat 객체를 값으로 가지는 딕셔너리
        
    Returns:
        torch.Tensor: 모든 버프의 Stat 값을 연결한 1차원 텐서
    """
    # 정렬된 버프 이름 목록
    if buff is None:
        return torch.zeros(len(_ordered_stat_keys), dtype=torch.float32)

    return encode_stat_as_tensor(buff)


def encode_running_as_tensor(running: dict[str, Running]) -> torch.Tensor:
    """
    실행 중인 스킬 딕셔너리를 PyTorch 텐서로 변환합니다.
    
    Args:
        running (dict[str, Running]): 스킬 이름을 키로, Running 객체를 값으로 가지는 딕셔너리
        
    Returns:
        torch.Tensor: 모든 실행 중인 스킬의 상태를 연결한 1차원 텐서
    """
    # 정렬된 스킬 이름 목록
    skill_names = sorted(running.keys())
    
    # 각 스킬의 Running 상태를 텐서로 변환하고 연결
    running_tensors = []
    for name in skill_names:
        running_state = running[name]
        running_tensors.append(torch.tensor([
            running_state.time_left / 1000,
            running_state.lasting_duration / 1000,
            running_state.stack if running_state.stack is not None else 0.0
        ], dtype=torch.float32))
    
    return torch.cat(running_tensors)


def encode_keydown_as_tensor(keydown: dict[str, KeydownView]) -> torch.Tensor:
    """
    키다운 상태 딕셔너리를 PyTorch 텐서로 변환합니다.
    
    Args:
        keydown (dict[str, KeydownView]): 스킬 이름을 키로, KeydownView 객체를 값으로 가지는 딕셔너리
        
    Returns:
        torch.Tensor: 모든 키다운 상태를 연결한 1차원 텐서
    """
    if len(keydown) == 0:
        return torch.zeros(1, dtype=torch.float32)

    # 정렬된 스킬 이름 목록
    skill_names = sorted(keydown.keys())
    
    # 각 스킬의 키다운 상태를 텐서로 변환하고 연결
    keydown_tensors = []
    for name in skill_names:
        keydown_state = keydown[name]
        keydown_tensors.append(torch.tensor([
            keydown_state.time_left / 1000,
            float(keydown_state.running)
        ], dtype=torch.float32))
    

    return torch.cat(keydown_tensors)


def encode_info_as_tensor(info: dict[str, ComponentInformation]) -> torch.Tensor:
    """
    컴포넌트 정보 딕셔너리를 PyTorch 텐서로 변환합니다.
    
    Args:
        info (dict[str, ComponentInformation]): 컴포넌트 이름을 키로, ComponentInformation 객체를 값으로 가지는 딕셔너리
        
    Returns:
        torch.Tensor: 모든 컴포넌트 정보를 연결한 1차원 텐서
    """
    # 정렬된 컴포넌트 이름 목록
    component_names = sorted(info.keys())
    
    # 각 컴포넌트의 정보를 텐서로 변환하고 연결
    info_tensors = []
    for name in component_names:
        component_info = info[name]
        # props는 딕셔너리이므로, 이를 평탄화하여 텐서로 변환
        props_values = []
        for value in component_info.props.values():
            if isinstance(value, (int, float)):
                props_values.append(float(value))
            elif isinstance(value, dict):
                # 딕셔너리의 값들을 재귀적으로 평탄화
                for v in value.values():
                    if isinstance(v, (int, float)):
                        props_values.append(float(v))

        info_tensors.append(torch.tensor(props_values, dtype=torch.float32))

    return torch.cat(info_tensors)

