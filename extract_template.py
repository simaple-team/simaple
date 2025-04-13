import yaml
import re
from typing import Dict, List, Tuple, Any # Any 추가

# --- 기존 코드 (extract_number, extract_values_from_template, generate_template_from_integers, process_skill_info) ---
# 여기에 위에 제공된 기존 함수들을 붙여넣으세요.
# ... (이전 코드 생략) ...

def extract_number(text: str, start: int) -> Tuple[str, int]:
    """숫자만 추출하고 다음 위치를 반환합니다."""
    num = ""
    i = start
    while i < len(text) and text[i].isdigit():
        num += text[i]
        i += 1
    return num, i


def extract_values_from_template(text, template):
    """
    템플릿을 기반으로 텍스트에서 값을 추출합니다.

    Args:
        text (str): 값을 추출할 원본 텍스트입니다.
        template (str): 추출할 값의 위치를 나타내는 플레이스홀더({name})가 포함된 템플릿 문자열입니다.

    Returns:
        dict or None: 플레이스홀더 이름을 키로, 추출된 값을 값으로 하는 딕셔너리입니다.
                      매칭되지 않으면 None을 반환합니다.
                      추출된 값은 가능한 경우 int 또는 float으로 변환됩니다.
    """
    # 1. 템플릿의 특수 문자를 이스케이프 처리합니다.
    escaped_template = re.escape(template)

    # 2. 이스케이프된 템플릿에서 플레이스홀더 부분을 정규식 캡처 그룹으로 변환합니다.
    placeholder_pattern = re.compile(r"\\\{([^{}]+?)\\}") # \{name\} 형태의 이스케이프된 플레이스홀더 찾기
    regex_pattern_parts = []
    last_end = 0
    var_names = []

    for match in placeholder_pattern.finditer(escaped_template):
        var_name = match.group(1)
        start = match.start()
        end = match.end()

        regex_pattern_parts.append(escaped_template[last_end:start])
        regex_pattern_parts.append(f"(?P<{var_name}>.*?)")
        var_names.append(var_name)
        last_end = end

    regex_pattern_parts.append(escaped_template[last_end:])
    final_regex_pattern = "^" + "".join(regex_pattern_parts) + "$"

    # 3. 생성된 정규식 패턴으로 텍스트를 매칭합니다.
    match = re.match(final_regex_pattern, text, re.DOTALL) # re.DOTALL 추가하여 줄바꿈 문자도 매칭

    if not match:
        return None

    # 4. 매칭된 결과를 추출하고, 가능한 경우 숫자 타입으로 변환합니다.
    extracted_data = {}
    raw_results = match.groupdict()

    for name, value_str in raw_results.items():
        value_str = value_str.strip()
        try:
            extracted_data[name] = int(value_str)
        except ValueError:
            try:
                extracted_data[name] = float(value_str)
            except ValueError:
                extracted_data[name] = value_str

    return extracted_data


def generate_template_from_integers(text):
    """
    텍스트에서 모든 정수 값을 찾아 순서대로 {vN} 플레이스홀더로 대체하여
    템플릿 문자열을 생성합니다. 음수도 처리합니다.

    Args:
        text (str): 원본 텍스트 문자열입니다.

    Returns:
        str: 정수가 플레이스홀더로 대체된 템플릿 문자열입니다.
             만약 텍스트에 정수가 없다면 원본 텍스트를 그대로 반환합니다.
    """
    if text is None: # text가 None인 경우 처리
        return ""
        
    template_parts = []
    last_end = 0
    v_index = 1
    # 음수를 포함한 정수를 찾는 정규식 수정: -?\d+
    for match in re.finditer(r'-?\d+', text):
        start, end = match.span()
        template_parts.append(text[last_end:start])
        template_parts.append(f"{{v{v_index}}}")
        v_index += 1
        last_end = end

    template_parts.append(text[last_end:])
    template = "".join(template_parts)

    # 만약 정수가 하나도 없었다면 v_index는 1 그대로일 것이므로 원본 반환
    # (또는 template이 원본 text와 동일할 것임)
    # if v_index == 1:
    #     return text
    return template


def process_skill_info(skill_info: Dict) -> Dict:
    """skill_info 데이터를 처리하여 템플릿과 레벨별 파라미터를 생성합니다."""
    result = {}

    for skill_name, skill_data in skill_info.items():
        if not skill_data:
            continue

        # None이 아닌 첫 번째 skill_effect를 기준으로 template 생성
        base_effect = None
        for data in skill_data:
            if data.get('skill_effect') is not None: # .get()으로 안전하게 접근
                base_effect = data['skill_effect']
                break

        if base_effect is None:
            print(f"Warning: Skill '{skill_name}' has no valid skill_effect found. Skipping.")
            continue # 유효한 base_effect가 없으면 스킵

        result[skill_name] = {}
        template = generate_template_from_integers(base_effect)

        params = {}
        for target_data in skill_data:
            # skill_effect가 None인 경우 스킵
            current_effect = target_data.get('skill_effect')
            if current_effect is None:
                print(f"Warning: Skill '{skill_name}', level {target_data.get('level')} has None skill_effect. Skipping extraction.")
                continue

            extracted_data = extract_values_from_template(
                current_effect, # None이 아닌 현재 효과 사용
                template
            )
            if extracted_data is None:
                # 추출 실패 시 경고 메시지 출력 (디버깅에 유용)
                print(f"Warning: Failed to extract values for skill '{skill_name}', level {target_data.get('level')} using template.")
                print(f"  Text: {current_effect}")
                print(f"  Template: {template}")
                continue

            level = target_data.get('level')
            if level is None:
                print(f"Warning: Missing level for skill '{skill_name}'. Skipping data.")
                continue

            for key, value in extracted_data.items():
                params.setdefault(key, {})
                params[key][level] = value

        result[skill_name]["template"] = template
        result[skill_name]["levels"] = params

    return result

# --- 새로 추가된 함수 ---
def postprocess_skill_info(processed_data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    처리된 스킬 데이터에서 값이 모든 레벨에서 동일한 변수를 찾아
    템플릿에 상수로 포함시키고 levels 딕셔너리에서 제거합니다.

    Args:
        processed_data (Dict): process_skill_info 함수로부터 반환된 딕셔너리.

    Returns:
        Dict: 상수 변수가 템플릿에 통합되고 levels에서 제거된 딕셔너리.
    """
    # 원본 딕셔너리를 직접 수정하지 않기 위해 깊은 복사 (선택 사항)
    # import copy
    # result_copy = copy.deepcopy(processed_data)
    # 여기서는 원본을 직접 수정하는 방식으로 진행합니다.

    skills_to_remove_from_levels = {} # {skill_name: [var_name1, var_name2, ...]}

    for skill_name, skill_details in processed_data.items():
        if "levels" not in skill_details or not skill_details["levels"]:
            continue # levels 정보가 없으면 건너뜀

        template = skill_details["template"]
        levels = skill_details["levels"]
        constants_found = {} # {var_name: constant_value}
        vars_to_remove = []

        for var_name, level_values in levels.items():
            if not level_values: # 특정 변수에 대한 레벨 데이터가 비어있으면 건너뜀
                continue

            # 모든 레벨의 값들을 set으로 만들어 길이가 1인지 확인
            unique_values = set(level_values.values())

            if len(unique_values) == 1:
                # 값이 하나뿐이면 상수임
                constant_value = unique_values.pop() # 유일한 값 추출
                constants_found[var_name] = constant_value
                vars_to_remove.append(var_name)
                # print(f"  [Constant Found] Skill: {skill_name}, Var: {var_name}, Value: {constant_value}") # 디버깅용

        # 상수 값을 템플릿에 직접 삽입
        if constants_found:
            new_template = template
            for var_name, const_value in constants_found.items():
                placeholder = f"{{{var_name}}}"
                # 템플릿 내 플레이스홀더를 실제 값(문자열 형태)으로 교체
                new_template = new_template.replace(placeholder, str(const_value))

            skill_details["template"] = new_template # 수정된 템플릿 저장

            # skills_to_remove_from_levels 딕셔너리에 제거할 변수 추가
            skills_to_remove_from_levels[skill_name] = vars_to_remove

    # levels 딕셔너리에서 상수 변수 제거 (템플릿 수정 후 별도 루프에서 처리)
    for skill_name, vars_to_remove in skills_to_remove_from_levels.items():
        levels = processed_data[skill_name]["levels"]
        for var_name in vars_to_remove:
            if var_name in levels:
                del levels[var_name]

        # 만약 모든 변수가 상수가 되어 levels 딕셔너리가 비게 되면 levels 키 자체를 제거 (선택 사항)
        if not levels:
            del processed_data[skill_name]["levels"]


    return processed_data


def main():
    # skill_info.yaml 파일 읽기
    try:
        with open('refs/skill_info.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: 'refs/skill_info.yaml' not found.")
        return
    except yaml.YAMLError as e:
        print(f"Error reading YAML file: {e}")
        return

    # response_at_6 필드 처리
    skill_info = data.get('skill_info', {}).get('response_at_6', {})
    if not skill_info:
       print("Warning: 'response_at_6' data not found or empty in skill_info.yaml")
       skill_info = {} # 빈 딕셔너리로 처리 계속 진행

    # 1단계: 템플릿 생성 및 레벨별 값 추출
    result = process_skill_info(skill_info)

    # 2단계: 상수 변수 처리
    final_result = postprocess_skill_info(result) # 후처리 함수 호출

    # 결과를 skill_template.yaml에 저장
    try:
        with open('skill_template.yaml', 'w', encoding='utf-8') as f:
            # yaml.dump 설정: allow_unicode=True (한글 유지), sort_keys=False (키 순서 유지)
            # default_flow_style=False (블록 스타일 YAML 선호)
            yaml.dump(final_result, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print("Successfully generated skill_template.yaml")
    except IOError as e:
        print(f"Error writing to skill_template.yaml: {e}")

if __name__ == '__main__':
    main()