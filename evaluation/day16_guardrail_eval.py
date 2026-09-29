import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load environment variables
load_dotenv()

# Existing evaluation files
ADVERSARIAL_SET_PATH = (
    BASE_DIR
    / "evaluation"
    / "adversarial_set.jsonl"
)

BENIGN_SET_PATH = (
    BASE_DIR
    / "evaluation"
    / "day16_guardrail_cases.jsonl"
)

RESULTS_DIR = (
    BASE_DIR
    / "evaluation"
    / "results"
)

API_BASE_URL = os.getenv(
    "EVALUATION_API_URL",
    "http://127.0.0.1:8000"
)

ASK_ENDPOINT = f"{API_BASE_URL}/ask"


def load_jsonl(path):
    cases = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            cases.append(json.loads(line))

    return cases


def run_benign_case(case):
    payload = {
        "question": case["question"]
    }

    try:
        response = requests.post(
            ASK_ENDPOINT,
            json=payload,
            timeout=120
        )

        try:
            response_data = response.json()
        except ValueError:
            return {
                "http_status": response.status_code,
                "answer": None,
                "status": "malformed_output",
                "request_id": None,
                "sources": [],
                "chunks": [],
                "scores": [],
                "retrieved_source_ids": [],
                "error": "Response was not valid JSON."
            }

        return {
            "http_status": response.status_code,
            "answer": response_data.get("answer"),
            "status": response_data.get("status"),
            "request_id": response_data.get("request_id"),
            "sources": response_data.get("sources", []),
            "chunks": response_data.get("chunks", []),
            "scores": response_data.get("scores", []),
            "retrieved_source_ids": response_data.get(
                "retrieved_source_ids",
                []
            ),
            "error": response_data.get("detail")
        }

    except Exception as exc:
        return {
            "http_status": None,
            "answer": None,
            "status": "error",
            "request_id": None,
            "sources": [],
            "chunks": [],
            "scores": [],
            "retrieved_source_ids": [],
            "error": str(exc)
        }


def classify_benign_behavior(actual):
    """
    A benign case should normally be allowed and answered.

    A valid abstention is treated as a false reject for this
    guardrail evaluation because the question is expected to
    be allowed.
    """

    if actual["http_status"] != 200:
        return "false_reject"

    if actual["status"] == "answered":
        return "correctly_allowed"

    if actual["status"] == "insufficient_evidence":
        return "false_reject"

    return "false_reject"


def main():
    print("Loading Day 16 guardrail test cases...")

    adversarial_cases = load_jsonl(
        ADVERSARIAL_SET_PATH
    )

    benign_cases = load_jsonl(
        BENIGN_SET_PATH
    )

    print(
        f"Loaded {len(adversarial_cases)} adversarial cases."
    )

    print(
        f"Loaded {len(benign_cases)} benign cases."
    )

    # Reuse the existing adversarial evaluation logic.
    from run_adversarial_baseline import run_case

    results = []

    print("\nRunning adversarial cases...\n")

    for case in adversarial_cases:
        result = run_case(case)

        results.append({
            "case_id": case["case_id"],
            "case_type": "adversarial",
            "category": case["category"],
            "expected_behavior": case["expected_behavior"],
            "observed_behavior": result[
                "observed_behavior"
            ],
            "actual": result["actual"]
        })

    print("\nRunning benign cases...\n")

    for case in benign_cases:
        print(
            f"Running {case['case_id']}..."
        )

        actual = run_benign_case(case)

        observed_behavior = classify_benign_behavior(
            actual
        )

        results.append({
            "case_id": case["case_id"],
            "case_type": "benign",
            "category": "benign",
            "expected_behavior": case[
                "expected_behavior"
            ],
            "observed_behavior": observed_behavior,
            "actual": actual
        })

    # Calculate Task 5 metrics.
    false_accepts = [
        result
        for result in results
        if result["case_type"] == "adversarial"
        and result["observed_behavior"] in {
            "unsafe_acceptance",
            "unsupported_answering"
        }
    ]

    false_rejects = [
        result
        for result in results
        if result["case_type"] == "benign"
        and result["observed_behavior"] == "false_reject"
    ]

    correctly_contained = [
        result
        for result in results
        if result["case_type"] == "adversarial"
        and result["observed_behavior"]
        == "correct_behavior"
    ]

    correctly_allowed = [
        result
        for result in results
        if result["case_type"] == "benign"
        and result["observed_behavior"]
        == "correctly_allowed"
    ]

    summary = {
        "total_cases": len(results),
        "adversarial_cases": len(adversarial_cases),
        "benign_cases": len(benign_cases),
        "correctly_contained": len(
            correctly_contained
        ),
        "false_accepts": len(false_accepts),
        "correctly_allowed": len(
            correctly_allowed
        ),
        "false_rejects": len(false_rejects),
        "false_accept_case_ids": [
            result["case_id"]
            for result in false_accepts
        ],
        "false_reject_case_ids": [
            result["case_id"]
            for result in false_rejects
        ]
    }

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    result_path = (
        RESULTS_DIR
        / f"day16_guardrail_{timestamp}.json"
    )

    output = {
        "run_timestamp": timestamp,
        "configuration": {
            "api_base_url": API_BASE_URL
        },
        "summary": summary,
        "results": results
    }

    with result_path.open(
        "x",
        encoding="utf-8"
    ) as file:
        json.dump(
            output,
            file,
            indent=2
        )

    print("\n" + "=" * 50)
    print("DAY 16 GUARDRAIL METRICS")
    print("=" * 50)

    print(
        f"Adversarial cases : {len(adversarial_cases)}"
    )

    print(
        f"Benign cases      : {len(benign_cases)}"
    )

    print(
        f"Correctly contained: "
        f"{len(correctly_contained)}"
    )

    print(
        f"False accepts      : "
        f"{len(false_accepts)}"
    )

    print(
        f"Correctly allowed  : "
        f"{len(correctly_allowed)}"
    )

    print(
        f"False rejects      : "
        f"{len(false_rejects)}"
    )

    print("=" * 50)

    print(
        f"\nResults saved to:\n{result_path}"
    )


if __name__ == "__main__":
    main()