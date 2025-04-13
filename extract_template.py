import yaml
import re
from typing import Dict, List, Tuple, Any
import math # math.isclose 사용 가능성 (여기서는 직접 비교)

# scipy.stats.linregress 를 사용하기 위해 import
try:
    from scipy.stats import linregress
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Warning: scipy library not found. Level equation regression requires 'pip install scipy'.")
    # scipy가 없으면 linregress를 사용하는 함수는 작동하지 않습니다.
    # 간단한 대체 구현을 시도하거나, 함수 실행을 건너뛸 수 있습니다.
    # 여기서는 함수 실행 시 오류를 발생시키도록 둡니다.

# --- 기존 코드 (extract_number, extract_values_from_template, generate_template_from_integers, process_skill_info, postprocess_skill_info) ---
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

    # 3. 생성된 정규식 패턴으로 텍스트를 매칭합니다. (re.DOTALL 추가)
    match = re.match(final_regex_pattern, text, re.DOTALL)

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
    if text is None:
        return ""

    template_parts = []
    last_end = 0
    v_index = 1
    for match in re.finditer(r'-?\d+', text):
        start, end = match.span()
        template_parts.append(text[last_end:start])
        template_parts.append(f"{{v{v_index}}}")
        v_index += 1
        last_end = end

    template_parts.append(text[last_end:])
    template = "".join(template_parts)

    return template

def process_skill_info(skill_info: Dict) -> Dict:
    """skill_info 데이터를 처리하여 템플릿과 레벨별 파라미터를 생성합니다."""
    result = {}

    for skill_name, skill_data in skill_info.items():
        if not skill_data:
            continue

        base_effect = None
        for data in skill_data:
            if data.get('skill_effect') is not None:
                base_effect = data['skill_effect']
                break

        if base_effect is None:
            print(f"Warning: Skill '{skill_name}' has no valid skill_effect found. Skipping.")
            continue

        result[skill_name] = {}
        template = generate_template_from_integers(base_effect)

        params = {}
        for target_data in skill_data:
            current_effect = target_data.get('skill_effect')
            if current_effect is None:
                # print(f"Warning: Skill '{skill_name}', level {target_data.get('level')} has None skill_effect. Skipping extraction.")
                continue

            extracted_data = extract_values_from_template(current_effect, template)

            if extracted_data is None:
                # print(f"Warning: Failed to extract values for skill '{skill_name}', level {target_data.get('level')} using template.")
                # print(f"  Text: {current_effect}")
                # print(f"  Template: {template}")
                continue

            level = target_data.get('level')
            if level is None:
                # print(f"Warning: Missing level for skill '{skill_name}'. Skipping data.")
                continue

            for key, value in extracted_data.items():
                params.setdefault(key, {})
                params[key][level] = value

        result[skill_name]["template"] = template
        result[skill_name]["levels"] = params

    return result

def postprocess_skill_info(processed_data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    처리된 스킬 데이터에서 값이 모든 레벨에서 동일한 변수를 찾아
    템플릿에 상수로 포함시키고 levels 딕셔너리에서 제거합니다.
    """
    skills_to_remove_from_levels = {}

    for skill_name, skill_details in processed_data.items():
        if "levels" not in skill_details or not skill_details["levels"]:
            continue

        template = skill_details["template"]
        levels = skill_details["levels"]
        constants_found = {}
        vars_to_remove = []

        for var_name, level_values in levels.items():
            if not level_values:
                continue

            unique_values = set(level_values.values())

            if len(unique_values) == 1:
                constant_value = unique_values.pop()
                constants_found[var_name] = constant_value
                vars_to_remove.append(var_name)

        if constants_found:
            new_template = template
            for var_name, const_value in constants_found.items():
                placeholder = f"{{{var_name}}}"
                new_template = new_template.replace(placeholder, str(const_value))
            skill_details["template"] = new_template
            skills_to_remove_from_levels[skill_name] = vars_to_remove

    for skill_name, vars_to_remove in skills_to_remove_from_levels.items():
        levels = processed_data[skill_name]["levels"]
        for var_name in vars_to_remove:
            if var_name in levels:
                del levels[var_name]
        if not levels:
           # levels가 비면 키 자체를 제거할 수도 있음 (선택적)
           # del processed_data[skill_name]["levels"]
           pass # 여기서는 비어있는 levels 딕셔너리를 남겨둠

    return processed_data

# --- 새로 추가된 함수 ---
def regress_level_equation(
    processed_data: Dict[str, Dict[str, Any]],
    max_divisor: int = 5, # 테스트할 divisor의 최대값
    error_threshold: float = 1e-6 # 허용 오차 (거의 0이어야 함)
) -> Dict[str, Dict[str, Any]]:
    """
    각 스킬 변수의 레벨-값 데이터를 기반으로
    value = (level // divisor) * a + b 형태의 관계식을 추정합니다.

    Args:
        processed_data (Dict): postprocess_skill_info 결과 딕셔너리.
        max_divisor (int): 테스트할 최대 divisor 값.
        error_threshold (float): 관계식이 성립한다고 판단할 최대 오차 합계.

    Returns:
        Dict: 각 스킬에 level_equations 키가 추가된 딕셔너리.
              (수정은 입력 딕셔너리에 직접 적용됨)
    """
    if not SCIPY_AVAILABLE:
        print("Error: regress_level_equation requires the 'scipy' library. Skipping equation regression.")
        return processed_data # scipy 없으면 원본 데이터 반환

    for skill_name, skill_details in processed_data.items():
        if "levels" not in skill_details or not skill_details["levels"]:
            continue

        level_equations = {}
        levels_data = skill_details["levels"]

        for var_name, level_values in levels_data.items():
            if len(level_values) < 2: # 최소 2개의 데이터 포인트 필요
                continue

            # 데이터 포인트 준비 (레벨 기준 정렬)
            points = sorted(level_values.items())
            levels = [p[0] for p in points]
            values = [p[1] for p in points]

            best_fit = None
            min_total_error = float('inf')

            # 다양한 divisor 값 시도
            for divisor in range(1, max_divisor + 1):
                # x 값 변환: level // divisor
                transformed_levels = [lvl // divisor for lvl in levels]

                # 변환된 x 값들이 최소 2개 이상 유니크해야 회귀 분석 가능
                if len(set(transformed_levels)) < 2:
                    # 모든 x값이 같다면, 모든 y값도 같은지 확인 (a=0, b=상수)
                    if len(set(values)) == 1:
                        current_a = 0
                        current_b = values[0] # 모든 값이 같으므로 첫번째 값 사용
                        # 이 경우의 오차 계산
                        total_error = sum(abs(v - ((l // divisor) * current_a + current_b)) for l, v in zip(levels, values))
                    else:
                        # x는 같은데 y가 다르면 회귀 불가
                        continue # 다음 divisor 시도
                else:
                    # 선형 회귀 수행: values = a * transformed_levels + b
                    try:
                        slope, intercept, r_value, p_value, std_err = linregress(transformed_levels, values)

                        # 계수는 정수일 것으로 예상되므로 반올림
                        current_a = round(slope)
                        current_b = round(intercept)

                        # 반올림된 정수 계수로 실제 오차 계산
                        total_error = sum(abs(v - ((l // divisor) * current_a + current_b)) for l, v in zip(levels, values))

                    except ValueError:
                        # linregress 실패 시 (예: 수직선 데이터)
                        continue # 다음 divisor 시도

                # 현재 divisor에서의 오차가 더 작으면 최고 기록 업데이트
                # 오차가 매우 작아야 유효한 식으로 간주
                if total_error < min_total_error:
                    min_total_error = total_error
                    # 오차가 임계값 이하일 때만 유효한 fit으로 저장 후보
                    if total_error <= error_threshold:
                        best_fit = {
                            "a": current_a,
                            "b": current_b,
                            "divisor": divisor,
                            "error": total_error
                        }
                    else:
                         # 오차가 임계값보다 크면, 일단 최소 오차는 기록하되 best_fit은 초기화
                         # (더 작은 오차가 나올 수 있지만, 임계값을 넘으면 최종 채택 안함)
                         best_fit = None # Reset best fit if error threshold is exceeded

            # 가장 적합한 fit (오차가 임계값 이하인)을 찾았으면 결과 저장
            if best_fit:
                a = best_fit["a"]
                b = best_fit["b"]
                divisor = best_fit["divisor"]

                # 방정식 문자열 생성 (가독성 개선)
                equation_parts = []
                if a != 0:
                    term1 = f"(skill_level // {divisor})"
                    if a != 1:
                        term1 += f" * {a}"
                    equation_parts.append(term1)

                if b != 0 or not equation_parts: # b가 0이 아니거나, a항이 없으면 b 출력 (a=0인 경우)
                    sign = "+" if b > 0 else "-"
                    # a항이 있고 b가 0이 아니면 부호와 공백 추가
                    prefix = f" {sign} " if equation_parts else (sign if b < 0 else "")
                    equation_parts.append(f"{prefix}{abs(b)}")

                equation = "".join(equation_parts)
                # 만약 a=0, b=0 이면 equation = "0"
                if not equation: equation = "0"


                level_equations[var_name] = {
                    "a": a,
                    "b": b,
                    "divisor": divisor,
                    "equation": equation
                }
            # else: # 디버깅: 적합한 식을 못 찾은 경우 로그 출력
            #     print(f"Info: Could not find a fitting equation for {skill_name} - {var_name} (min error: {min_total_error:.4f})")


        # 해당 스킬에 대해 찾은 방정식들이 있으면 결과 딕셔너리에 추가
        if level_equations:
            skill_details["level_equations"] = level_equations

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

    skill_info = data.get('skill_info', {}).get('response_at_6', {})
    if not skill_info:
       print("Warning: 'response_at_6' data not found or empty in skill_info.yaml")
       skill_info = {}

    # 1단계: 템플릿 생성 및 레벨별 값 추출
    result = process_skill_info(skill_info)

    # 2단계: 상수 변수 처리
    processed_result = postprocess_skill_info(result)

    # 3단계: 레벨 방정식 회귀 분석
    final_result = regress_level_equation(processed_result) # 회귀 함수 호출

    # 결과를 skill_template.yaml에 저장
    try:
        with open('skill_template.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(final_result, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print("Successfully generated skill_template.yaml with level equations.")
    except IOError as e:
        print(f"Error writing to skill_template.yaml: {e}")

if __name__ == '__main__':
    main()