import json
import sys
from pathlib import Path


# File paths
RESULTS_DIR = Path("evaluation/results")
SCORECARD_PATH = RESULTS_DIR / "scorecard.json"


# Minimum acceptable metrics
THRESHOLDS = {
    "overall_pass_rate": 0.60,
    "hit_at_3": 0.85,
    "recall_at_3": 0.85,
    "mrr": 0.85,
    "citation_validity_rate": 0.80,
    "abstention_accuracy": 0.90,
}


def load_scorecard():
    if not SCORECARD_PATH.exists():
        raise FileNotFoundError(
            f"Scorecard not found: {SCORECARD_PATH}"
        )

    with open(SCORECARD_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def get_metrics(scorecard):
    return {
        "overall_pass_rate": scorecard["overall_pass_rate"],
        "hit_at_3": scorecard["retrieval_metrics"]["hit_at_3"],
        "recall_at_3": scorecard["retrieval_metrics"]["recall_at_3"],
        "mrr": scorecard["retrieval_metrics"]["mrr"],
        "citation_validity_rate": (
            scorecard["citation_metrics"]["citation_validity_rate"]
        ),
        "abstention_accuracy": (
            scorecard["abstention"]["accuracy"]
        ),
    }


def check_thresholds(metrics):
    results = []

    for metric, minimum in THRESHOLDS.items():
        actual = metrics[metric]
        passed = actual >= minimum

        results.append(
            {
                "metric": metric,
                "actual": actual,
                "minimum": minimum,
                "passed": passed,
            }
        )

    return results


def print_results(results):
    print()
    print("DAY 14 - REGRESSION CHECK")
    print("-" * 70)

    for result in results:
        metric = result["metric"]
        actual = result["actual"]
        minimum = result["minimum"]

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"{metric:<28} "
            f"actual={actual:.2%} "
            f"minimum={minimum:.2%} "
            f"[{status}]"
        )

    print("-" * 70)


def main():
    scorecard = load_scorecard()
    metrics = get_metrics(scorecard)
    results = check_thresholds(metrics)

    print_results(results)

    failed_checks = [
        result
        for result in results
        if not result["passed"]
    ]

    if failed_checks:
        print()
        print("REGRESSION CHECK FAILED")
        print(
            f"{len(failed_checks)} critical threshold(s) "
            "were not satisfied."
        )

        return 1

    print()
    print("REGRESSION CHECK PASSED")
    print("All critical thresholds are satisfied.")

    return 0


if __name__ == "__main__":
    sys.exit(main())