import logging
import re
from pathlib import Path
from typing import Sequence, TypedDict

import yaml

# --- TypedDict Definitions ---


class SkillLevelDataInput(TypedDict):
    level: int
    skill_effect: str | None


SkillInfoInput = dict[str, list[SkillLevelDataInput]]

ExtractedValues = dict[str, int | float | str]
LevelValues = dict[int, int | float | str]  # Level -> Value
ProcessedLevels = dict[str, LevelValues]  # VarName -> LevelValues


class LevelEquation(TypedDict):
    a: int
    b: int
    divisor: int
    equation: str


SkillLevelEquations = dict[str, LevelEquation]  # VarName -> LevelEquation


class _ProcessedSkillData(TypedDict):
    template: str


class ProcessedSkillData(_ProcessedSkillData, total=False):
    levels: ProcessedLevels
    level_equations: SkillLevelEquations


FinalResult = dict[str, ProcessedSkillData]  # SkillName -> ProcessedSkillData

# --- SciPy Dependency Handling ---
try:
    from scipy.stats import linregress

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning(
        "scipy library not found. Level equation regression requires 'pip install scipy'. Skipping equation regression."
    )

# --- Helper Functions ---


def _escape_and_create_regex(template: str) -> tuple[re.Pattern | None, list[str]]:
    """Escapes template and creates a regex pattern with named capture groups."""
    try:
        escaped_template = re.escape(template)
        placeholder_pattern = re.compile(r"\\\{([^{}]+?)\\}")
        regex_pattern_parts = []
        last_end = 0
        var_names = []

        for match in placeholder_pattern.finditer(escaped_template):
            var_name = match.group(1)
            start, end = match.start(), match.end()
            regex_pattern_parts.append(escaped_template[last_end:start])
            regex_pattern_parts.append(f"(?P<{var_name}>.*?)")
            var_names.append(var_name)
            last_end = end

        regex_pattern_parts.append(escaped_template[last_end:])
        final_regex_string = "^" + "".join(regex_pattern_parts) + "$"
        # Add re.DOTALL to handle multiline skill effects
        return re.compile(final_regex_string, re.DOTALL), var_names
    except re.error as e:
        logging.error(f"Regex compilation failed for template: {template}\nError: {e}")
        return None, []


def _parse_value(value_str: str) -> int | float | str:
    """Tries to parse string value to int or float."""
    value_str = value_str.strip()
    try:
        return int(value_str)
    except ValueError:
        try:
            return float(value_str)
        except ValueError:
            return value_str  # Keep as string if parsing fails


def _calculate_equation_error(
    levels: Sequence[int],
    values: Sequence[int | float | str],
    a: int,
    b: int,
    divisor: int,
) -> float:
    """Calculates the total absolute error for the equation."""
    total_error = 0.0
    for lvl, val in zip(levels, values):
        # Ensure value is numeric for calculation
        if isinstance(val, (int, float)):
            predicted_val = (lvl // divisor) * a + b
            total_error += abs(val - predicted_val)
        else:
            # Handle non-numeric values if necessary, here we assume they shouldn't exist for regression
            logging.warning(
                f"Non-numeric value '{val}' encountered for level {lvl} during error calculation."
            )
            return float("inf")  # Indicate error or incompatibility
    return total_error


def _format_equation_string(a: int, b: int, divisor: int) -> str:
    """Formats the equation string for readability."""
    equation_parts = []
    if a != 0:
        if divisor != 1:
            term1 = f"(skill_level // {divisor})"
        else:
            term1 = "skill_level"
        if a != 1:
            # Handle negative 'a' cleanly in the string
            if a == -1:
                term1 = f"-{term1}"
            else:
                term1 += f" * {a}"
        equation_parts.append(term1)

    if b != 0 or not equation_parts:
        sign = "+" if b >= 0 else "-"
        # Add space only if a previous term exists and b is not zero
        prefix = f" {sign} " if equation_parts and b != 0 else (sign if b < 0 else "")
        # Add b if it's non-zero or if it's the only term (a=0 case)
        if b != 0 or not equation_parts:
            equation_parts.append(f"{prefix}{abs(b)}")

    equation = "".join(equation_parts)
    return equation if equation else "0"  # Return "0" if a=0 and b=0


# --- Core Logic Functions ---


def extract_values_from_template(text: str, template: str) -> ExtractedValues | None:
    """Extracts values from text based on the template using regex."""
    regex_pattern, _ = _escape_and_create_regex(template)
    if not regex_pattern or text is None:
        return None

    match = regex_pattern.match(text)
    if not match:
        return None

    raw_results = match.groupdict()
    extracted_data: ExtractedValues = {
        name: _parse_value(value_str) for name, value_str in raw_results.items()
    }
    return extracted_data


def generate_template_from_integers(text: str | None) -> str:
    """Generates a template string by replacing integers with placeholders."""
    if text is None:
        return ""

    template_parts = []
    last_end = 0
    v_index = 1
    # Regex to find integers (including negative)
    for match in re.finditer(r"-?\d+", text):
        start, end = match.span()
        template_parts.append(text[last_end:start])
        template_parts.append(f"{{v{v_index}}}")
        v_index += 1
        last_end = end

    template_parts.append(text[last_end:])
    return "".join(template_parts)


def process_skill_info(skill_info_input: SkillInfoInput) -> FinalResult:
    """Processes raw skill info to create templates and level parameters."""
    result: FinalResult = {}

    for skill_name, skill_level_data_list in skill_info_input.items():
        if not skill_level_data_list:
            continue

        base_effect: str | None = None
        for data in skill_level_data_list:
            if data.get("skill_effect") is not None:
                base_effect = data["skill_effect"]
                break

        if base_effect is None:
            logging.warning(
                f"Skill '{skill_name}': No valid skill_effect found. Skipping."
            )
            continue

        template = generate_template_from_integers(base_effect)
        if not template:
            logging.warning(
                f"Skill '{skill_name}': Failed to generate template. Skipping."
            )
            continue

        params: ProcessedLevels = {}
        skill_data: ProcessedSkillData = {"template": template}

        for target_data in skill_level_data_list:
            current_effect = target_data.get("skill_effect")
            level = target_data.get("level")

            if current_effect is None or level is None:
                continue

            extracted_data = extract_values_from_template(current_effect, template)

            if extracted_data is None:
                continue

            for key, value in extracted_data.items():
                params.setdefault(key, {})
                params[key][level] = value

        if params:
            skill_data["levels"] = params
        result[skill_name] = skill_data

    return result


def postprocess_remove_constants(processed_data: FinalResult) -> FinalResult:
    """Removes constant variables from levels and embeds them into the template."""
    skills_to_update: dict[str, list[str]] = {}  # SkillName -> [VarNamesToRemove]

    for skill_name, skill_details in processed_data.items():
        if "levels" not in skill_details or not skill_details["levels"]:
            continue

        template = skill_details["template"]
        levels = skill_details["levels"]
        constants_found: dict[str, int | float | str] = {}
        vars_to_remove: list[str] = []

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
                # Use replace with count=1 for safety, though not strictly needed here
                new_template = new_template.replace(placeholder, str(const_value))

            skill_details["template"] = new_template
            skills_to_update[skill_name] = vars_to_remove

    for skill_name, vars_to_remove in skills_to_update.items():
        if "levels" in processed_data[skill_name]:
            levels = processed_data[skill_name]["levels"]  # type: ignore
            for var_name in vars_to_remove:
                if var_name in levels:
                    del levels[var_name]
            # Optionally remove the 'levels' key if it becomes empty
            if not levels:
                del processed_data[skill_name]["levels"]

    return processed_data


def regress_level_equations(
    processed_data: FinalResult, max_divisor: int = 5, error_threshold: float = 1e-6
) -> FinalResult:
    """Regresses level equations of the form value = (level // divisor) * a + b."""
    if not SCIPY_AVAILABLE:
        return processed_data  # Skip if scipy is not available

    for skill_name, skill_details in processed_data.items():
        if "levels" not in skill_details or not skill_details["levels"]:
            continue

        level_equations: SkillLevelEquations = {}
        levels_data = skill_details["levels"]

        for var_name, level_values in levels_data.items():
            # Need at least two points with numeric values for regression
            numeric_points = {
                lvl: val
                for lvl, val in level_values.items()
                if isinstance(val, (int, float))
            }
            if len(numeric_points) < 2:
                continue

            points = sorted(numeric_points.items())
            levels = [p[0] for p in points]
            values = [p[1] for p in points]  # Now guaranteed numeric

            best_fit_params: LevelEquation | None = None
            min_total_error = float("inf")

            for divisor in range(1, max_divisor + 1):
                transformed_levels = [lvl // divisor for lvl in levels]

                # Need at least two unique transformed x-values for linregress
                if len(set(transformed_levels)) < 2:
                    # If all x are same, check if all y are same (a=0 case)
                    if len(set(values)) == 1:
                        current_a = 0
                        current_b = values[0]
                        total_error = _calculate_equation_error(
                            levels, values, current_a, current_b, divisor
                        )
                    else:
                        continue  # Cannot fit line if x is constant but y varies
                else:
                    try:
                        slope, intercept, r_value, p_value, std_err = linregress(
                            transformed_levels, values
                        )
                        current_a: int = round(slope)
                        current_b: int = round(intercept)
                        total_error = _calculate_equation_error(
                            levels, values, current_a, current_b, divisor
                        )
                    except ValueError:
                        continue  # linregress failed

                if total_error < min_total_error:
                    min_total_error = total_error
                    # Only consider fits below the error threshold as valid
                    if total_error <= error_threshold:
                        best_fit_params = {
                            "a": current_a,
                            "b": current_b,
                            "divisor": divisor,
                            "equation": _format_equation_string(
                                current_a, current_b, divisor
                            ),  # Format here
                        }
                    else:
                        best_fit_params = (
                            None  # Reset if error is too high, even if minimal so far
                        )

            if best_fit_params:
                level_equations[var_name] = best_fit_params
            # else:
            #     logging.info(f"Skill '{skill_name}', Var '{var_name}': Could not find fitting equation (min error: {min_total_error:.4f}).")

        if level_equations:
            skill_details["level_equations"] = level_equations
            skill_details.pop("levels")

    return processed_data


# --- Main Execution ---


def load_yaml_data(file_path: Path) -> dict | None:
    """Loads data from a YAML file."""
    if not file_path.is_file():
        logging.error(f"YAML file not found: {file_path}")
        return None
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        logging.error(f"Error reading YAML file {file_path}: {e}")
        return None
    except IOError as e:
        logging.error(f"Error opening YAML file {file_path}: {e}")
        return None


def save_yaml_data(data: dict, file_path: Path) -> bool:
    """Saves data to a YAML file."""
    try:
        with file_path.open("w", encoding="utf-8") as f:
            yaml.dump(
                data, f, allow_unicode=True, sort_keys=False, default_flow_style=False
            )
        logging.info(f"Successfully generated {file_path}")
        return True
    except IOError as e:
        logging.error(f"Error writing to YAML file {file_path}: {e}")
        return False
    except yaml.YAMLError as e:  # Should not happen with dump, but good practice
        logging.error(f"Error during YAML serialization for {file_path}: {e}")
        return False


def main():
    """Main function to process skill data and generate template file."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    input_yaml_path = Path("refs/skill_info.yaml")
    output_yaml_path = Path("skill_template.yaml")

    raw_data = load_yaml_data(input_yaml_path)
    if raw_data is None:
        return

    # Safely access nested structure
    skill_info_input: SkillInfoInput = raw_data.get("skill_info", {}).get(
        "response_at_6", {}
    )
    if not skill_info_input:
        logging.warning("'response_at_6' data not found or empty in skill_info.yaml")
        # Proceed with empty dict if not found

    # --- Processing Pipeline ---
    result_step1 = process_skill_info(skill_info_input)
    result_step2 = postprocess_remove_constants(result_step1)
    final_result = regress_level_equations(result_step2)

    save_yaml_data(final_result, output_yaml_path)


if __name__ == "__main__":
    main()
