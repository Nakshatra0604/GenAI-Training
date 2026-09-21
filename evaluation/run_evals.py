import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent


# Evaluation files
GOLDEN_SET_PATH = (
    BASE_DIR
    / "evaluation"
    / "golden_set.jsonl"
)

RESULTS_DIR = (
    BASE_DIR
    / "evaluation"
    / "results"
)


# API configuration
API_BASE_URL = os.getenv(
    "EVALUATION_API_URL",
    "http://127.0.0.1:8000"
)

ASK_ENDPOINT = f"{API_BASE_URL}/ask"

GENERATION_MODEL = os.getenv(
    "GENERATION_MODEL",
    "unknown"
)

PROMPT_VERSION = os.getenv(
    "PROMPT_VERSION",
    "unknown"
)


def load_golden_set():
    """
    Load evaluation cases from the golden dataset.
    """

    cases = []

    with GOLDEN_SET_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            if not line.strip():
                continue

            case = json.loads(line)
            cases.append(case)

    return cases


def run_case(case):
    """
    Send one evaluation case to the RAG API
    and return a structured evaluation result.
    """

    payload = {
        "question": case["question"]
    }

    started_at = time.perf_counter()

    try:
        response = requests.post(
            ASK_ENDPOINT,
            json=payload,
            timeout=120
        )

        latency_ms = (
            time.perf_counter() - started_at
        ) * 1000

        response_data = response.json()

        return {
            "http_status": response.status_code,

            "latency_ms": latency_ms,

            "answer": response_data.get(
                "answer"
            ),

            "citations": response_data.get(
                "sources",
                []
            ),

            "retrieval_results": {
                "chunks": response_data.get(
                    "chunks",
                    []
                ),
                "scores": response_data.get(
                    "scores",
                    []
                )
            },

            "status": response_data.get(
                "status"
            ),

            "request_id": response_data.get(
                "request_id"
            ),

            "error": None
        }

    except Exception as exc:

        latency_ms = (
            time.perf_counter() - started_at
        ) * 1000

        return {
            "http_status": None,

            "latency_ms": latency_ms,

            "answer": None,

            "citations": [],

            "retrieval_results": {
                "chunks": [],
                "scores": []
            },

            "status": "error",

            "request_id": None,

            "error": str(exc)
        }


def run_all_cases(cases):
    """
    Run all evaluation cases and collect results.
    """

    results = []

    for case in cases:

        print(
            f"Running {case['case_id']}..."
        )

        result = run_case(case)

        results.append(
            {
                "case_id": case["case_id"],
                "expected": case,
                "actual": result
            }
        )

    return results


def save_results(results):
    """
    Save evaluation results to a timestamped
    JSON artifact without overwriting earlier runs.
    """

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    result_path = (
        RESULTS_DIR
        / f"evaluation_run_{timestamp}.json"
    )

    output = {
        "run_timestamp": timestamp,

        "configuration": {
            "api_base_url": API_BASE_URL,
            "generation_model": (
                GENERATION_MODEL
            ),
            "prompt_version": PROMPT_VERSION
        },

        "total_cases": len(results),

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

    return result_path


if __name__ == "__main__":

    cases = load_golden_set()

    print(
        f"Loaded {len(cases)} evaluation cases."
    )

    results = run_all_cases(cases)

    print(
        f"Completed {len(results)} evaluation cases."
    )

    result_path = save_results(
        results
    )

    print(
        f"Results saved to: {result_path}"
    )