import json
import statistics
from pathlib import Path


# File paths
RESULTS_DIR = Path("evaluation/results")
REVIEW_REPORT_PATH = RESULTS_DIR / "review_report.json"


# Load the review report created in Task 3
def load_review_report():
    if not REVIEW_REPORT_PATH.exists():
        raise FileNotFoundError(
            f"Review report not found: {REVIEW_REPORT_PATH}"
        )

    with open(REVIEW_REPORT_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# Calculate a percentile from a list of values
def calculate_percentile(values, percentile):
    if not values:
        return None

    values = sorted(values)

    if len(values) == 1:
        return values[0]

    position = (len(values) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    fraction = position - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * fraction
    )


def percentage(value, total):
    if total == 0:
        return 0.0

    return (value / total) * 100


# Build the Day 14 scorecard
def build_scorecard():
    report = load_review_report()

    summary = report["summary"]
    cases = report["cases"]

    total_cases = summary["total_cases"]
    passed_cases = summary["passed_cases"]
    failed_cases = summary["failed_cases"]

    pass_rate = summary["pass_rate"]

    # Retrieval metrics use answerable cases only
    answerable_cases = [
        case
        for case in cases
        if case["expected_answerable"] is True
    ]

    retrieval_total = len(answerable_cases)

    hit_at_3 = (
        sum(
            case["retrieval"]["hit_at_3"]
            for case in answerable_cases
        )
        / retrieval_total
        if retrieval_total
        else 0
    )

    recall_at_3 = (
        sum(
            case["retrieval"]["recall_at_3"]
            for case in answerable_cases
        )
        / retrieval_total
        if retrieval_total
        else 0
    )

    mrr = (
        sum(
            case["retrieval"]["mrr"]
            for case in answerable_cases
        )
        / retrieval_total
        if retrieval_total
        else 0
    )

    # Citation metrics apply to answerable cases
    citation_cases = [
        case
        for case in cases
        if case["expected_answerable"] is True
    ]

    citation_total = len(citation_cases)

    citation_presence_pass = sum(
        1
        for case in citation_cases
        if case["answer"]["citation_presence_pass"] is True
    )

    citation_validity_pass = sum(
        1
        for case in citation_cases
        if case["answer"]["citation_validity_pass"] is True
    )

    citation_presence_rate = percentage(
        citation_presence_pass,
        citation_total,
    )

    citation_validity_rate = percentage(
        citation_validity_pass,
        citation_total,
    )

    # Required-fact coverage applies only to cases with required facts
    fact_cases = [
        case
        for case in cases
        if case["expected_answerable"] is True
        and case["answer"]["required_facts_pass"] is not None
    ]

    required_facts_pass = sum(
        1
        for case in fact_cases
        if case["answer"]["required_facts_pass"] is True
    )

    required_facts_rate = percentage(
        required_facts_pass,
        len(fact_cases),
    )

    # Abstention accuracy uses all cases
    abstention_correct = sum(
        1
        for case in cases
        if case["answer"]["abstention_pass"] is True
    )

    abstention_accuracy = percentage(
        abstention_correct,
        total_cases,
    )

    # Failure category counts
    failure_categories = {}

    for case in cases:
        if case["overall_result"] != "FAIL":
            continue

        category = case["primary_failure_category"]

        failure_categories[category] = (
            failure_categories.get(category, 0) + 1
        )

    # Latency metrics
    latencies = [
        case["latency_ms"]
        for case in cases
        if isinstance(case.get("latency_ms"), (int, float))
    ]

    if latencies:
        average_latency = statistics.mean(latencies)
        minimum_latency = min(latencies)
        maximum_latency = max(latencies)
        p95_latency = calculate_percentile(latencies, 0.95)
    else:
        average_latency = None
        minimum_latency = None
        maximum_latency = None
        p95_latency = None

    # Cost proxy based on evaluation request count
    cost_proxy = {
        "type": "evaluation_request_count",
        "value": total_cases,
        "unit": "requests",
    }

    scorecard = {
        "report_name": "Day 14 Evaluation Scorecard",
        "source_report": str(REVIEW_REPORT_PATH),
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": failed_cases,
        "overall_pass_rate": pass_rate,

        "retrieval_metrics": {
            "evaluated_cases": retrieval_total,
            "hit_at_3": round(hit_at_3, 4),
            "recall_at_3": round(recall_at_3, 4),
            "mrr": round(mrr, 4),
        },

        "citation_metrics": {
            "evaluated_cases": citation_total,
            "citation_presence_rate": round(
                citation_presence_rate / 100,
                4,
            ),
            "citation_validity_rate": round(
                citation_validity_rate / 100,
                4,
            ),
        },

        "required_facts": {
            "evaluated_cases": len(fact_cases),
            "pass_rate": round(
                required_facts_rate / 100,
                4,
            ),
        },

        "abstention": {
            "evaluated_cases": total_cases,
            "correct_cases": abstention_correct,
            "accuracy": round(
                abstention_accuracy / 100,
                4,
            ),
        },

        "failure_categories": failure_categories,

        "latency_ms": {
            "cases_with_latency": len(latencies),
            "average": (
                round(average_latency, 2)
                if average_latency is not None
                else None
            ),
            "minimum": (
                round(minimum_latency, 2)
                if minimum_latency is not None
                else None
            ),
            "maximum": (
                round(maximum_latency, 2)
                if maximum_latency is not None
                else None
            ),
            "p95": (
                round(p95_latency, 2)
                if p95_latency is not None
                else None
            ),
        },

        "cost_proxy": cost_proxy,
    }

    return scorecard


# Save the scorecard as JSON
def save_scorecard(scorecard):
    output_path = RESULTS_DIR / "scorecard.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            scorecard,
            file,
            indent=2,
        )

    return output_path


# Display the scorecard in the terminal
def print_scorecard(scorecard):
    print()
    print("DAY 14 - EVALUATION SCORECARD")
    print("-" * 70)

    print()
    print("Overall")
    print("-" * 30)
    print(f"Total cases:          {scorecard['total_cases']}")
    print(f"Passed cases:         {scorecard['passed_cases']}")
    print(f"Failed cases:         {scorecard['failed_cases']}")
    print(
        f"Pass rate:            "
        f"{scorecard['overall_pass_rate'] * 100:.2f}%"
    )

    retrieval = scorecard["retrieval_metrics"]

    print()
    print("Retrieval")
    print("-" * 30)
    print(f"Evaluated cases:      {retrieval['evaluated_cases']}")
    print(f"Hit@3:                {retrieval['hit_at_3'] * 100:.2f}%")
    print(f"Recall@3:             {retrieval['recall_at_3'] * 100:.2f}%")
    print(f"MRR:                  {retrieval['mrr'] * 100:.2f}%")

    citation = scorecard["citation_metrics"]

    print()
    print("Citation and Answer Quality")
    print("-" * 30)
    print(f"Evaluated cases:      {citation['evaluated_cases']}")
    print(
        f"Citation presence:   "
        f"{citation['citation_presence_rate'] * 100:.2f}%"
    )
    print(
        f"Citation validity:   "
        f"{citation['citation_validity_rate'] * 100:.2f}%"
    )

    facts = scorecard["required_facts"]

    print(
        f"Required facts:       "
        f"{facts['pass_rate'] * 100:.2f}%"
    )
    print(
        f"Fact cases evaluated: "
        f"{facts['evaluated_cases']}"
    )

    abstention = scorecard["abstention"]

    print()
    print("Abstention")
    print("-" * 30)
    print(
        f"Evaluated cases:      "
        f"{abstention['evaluated_cases']}"
    )
    print(
        f"Correct cases:        "
        f"{abstention['correct_cases']}"
    )
    print(
        f"Accuracy:             "
        f"{abstention['accuracy'] * 100:.2f}%"
    )

    print()
    print("Failure Categories")
    print("-" * 30)

    if scorecard["failure_categories"]:
        for category, count in sorted(
            scorecard["failure_categories"].items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            print(f"{category}: {count}")
    else:
        print("No failures recorded.")

    latency = scorecard["latency_ms"]

    print()
    print("Latency")
    print("-" * 30)

    if latency["average"] is not None:
        print(f"Average:              {latency['average']:.2f} ms")
        print(f"Minimum:              {latency['minimum']:.2f} ms")
        print(f"Maximum:              {latency['maximum']:.2f} ms")
        print(f"P95:                  {latency['p95']:.2f} ms")
    else:
        print("Latency data not available.")

    cost = scorecard["cost_proxy"]

    print()
    print("Cost Proxy")
    print("-" * 30)
    print(f"Requests:             {cost['value']}")
    print(f"Proxy type:           {cost['type']}")

    print()
    print("-" * 70)


if __name__ == "__main__":
    try:
        scorecard = build_scorecard()
        output_path = save_scorecard(scorecard)
        print_scorecard(scorecard)

        print()
        print(f"Scorecard saved to: {output_path}")

    except Exception as exc:
        print()
        print(f"Scorecard generation failed: {exc}")
        raise