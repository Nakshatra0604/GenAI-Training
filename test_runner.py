import json
import os

from validators import (
    validate_input,
    parse_summarization,
    parse_extraction,
    parse_classification,
    validate_output,
)

from model_client import generate_response


PROMPT_VERSION = "v2"


def load_test_cases():
    with open(
        "test_dataset/test_cases.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_results(results):
    os.makedirs("test_results", exist_ok=True)

    result_file = os.path.join(
        "test_results",
        "version_2_results.json"
    )

    with open(
        result_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(results, file, indent=4)


def compare_expected_values(parsed_data, expected_values):
    if not expected_values:
        return "NOT_EVALUATED", "No expected values provided."

    mismatches = []

    for field, expected_value in expected_values.items():
        actual_value = parsed_data.get(field)

        if actual_value != expected_value:
            mismatches.append(
                f"{field}: expected '{expected_value}', "
                f"got '{actual_value}'"
            )

    if mismatches:
        return "FAIL", "; ".join(mismatches)

    return "PASS", None


test_cases = load_test_cases()

print(f"Loaded {len(test_cases)} test cases.\n")

results = []

for case in test_cases:

    # -------------------------
    # 1. Validate input
    # -------------------------
    is_valid, error = validate_input(
        case["task"],
        case["input_type"],
        case["input"]
    )

    if not is_valid:
        print(
            f"{case['case_id']} - "
            f"Input Validation Failed: {error}"
        )

        results.append({
            "case_id": case["case_id"],
            "prompt_version": PROMPT_VERSION,
            "model_version": None,
            "latency": None,
            "model_response": None,
            "validation_result": "FAIL",
            "failure_reason": error,
            "task_accuracy": "NOT_EVALUATED",
            "accuracy_reason": "Input validation failed."
        })

        continue

    # -------------------------
    # 2. Load prompt template
    # -------------------------
    prompt_path = (
        f"prompts_templates/"
        f"{case['task']}_prompt.md"
    )

    with open(
        prompt_path,
        "r",
        encoding="utf-8"
    ) as file:
        prompt_template = file.read()

    final_prompt = prompt_template.replace(
        "{text}",
        case["input"]
    )

    # -------------------------
    # 3. Send prompt to model
    # -------------------------
    print(
        f"{case['case_id']} - "
        f"Sending to model..."
    )

    result = generate_response(final_prompt)

    print(
        f"{case['case_id']} - "
        f"Model response received"
    )

    # -------------------------
    # 4. Handle model failure
    # -------------------------
    if result["text"] is None:

        results.append({
            "case_id": case["case_id"],
            "prompt_version": PROMPT_VERSION,
            "model_version": result["model"],
            "latency": result["latency"],
            "model_response": None,
            "validation_result": "FAIL",
            "failure_reason": result.get("error", "MODEL_ERROR"),
            "task_accuracy": "NOT_EVALUATED",
            "accuracy_reason": "Model failed to return a response."
        })

        continue

    # -------------------------
    # 5. Store actual model response
    # -------------------------
    actual_response = result["text"]

    print(
        f"{case['case_id']} - "
        f"Actual Model Response:\n"
        f"{actual_response}\n"
    )

    # -------------------------
    # 6. Parse model response
    # -------------------------
    if case["task"] == "summarization":

        parsed_data = parse_summarization(
            actual_response
        )

    elif case["task"] == "extraction":

        parsed_data = parse_extraction(
            actual_response
        )

    elif case["task"] == "classification":

        parsed_data = parse_classification(
            actual_response
        )

    # -------------------------
    # 7. Validate output format
    # -------------------------
    validation_passed, validation_message = validate_output(
        case["task"],
        parsed_data,
        actual_response
    )

    if validation_passed:

        print(
            f"{case['case_id']} - "
            f"Output Validation Passed"
        )

        validation_result = "PASS"
        failure_reason = None

    else:

        print(
            f"{case['case_id']} - "
            f"Output Validation Failed: "
            f"{validation_message}"
        )

        validation_result = "FAIL"
        failure_reason = validation_message

    # -------------------------
    # 8. Compare expected values
    # -------------------------
    task_accuracy, accuracy_reason = compare_expected_values(
        parsed_data,
        case.get("expected_values", {})
    )

    print(
        f"{case['case_id']} - "
        f"Task Accuracy: {task_accuracy}"
    )

    if accuracy_reason:
        print(
            f"Accuracy Reason: {accuracy_reason}"
        )

    # -------------------------
    # 9. Save complete result
    # -------------------------
    results.append({
        "case_id": case["case_id"],
        "prompt_version": PROMPT_VERSION,
        "model_version": result["model"],
        "latency": result["latency"],
        "model_response": actual_response,
        "validation_result": validation_result,
        "failure_reason": failure_reason,
        "task_accuracy": task_accuracy,
        "accuracy_reason": accuracy_reason
    })


# -------------------------
# 10. Save machine-readable results
# -------------------------

save_results(results)

print("\nTest run completed.")
print(
    "Results saved to "
    "test_results/version_2_results.json"
)

