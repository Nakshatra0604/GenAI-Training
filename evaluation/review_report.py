"""
Day 14 - Review-Friendly Evaluation Report

Combines retrieval and answer evaluation results into one
per-case review-friendly report.

This script uses the latest saved evaluation JSON.
It does not call the RAG API or generate new answers.
"""

import json
from datetime import datetime
from pathlib import Path

from evaluation.retrieval_grader import (
    load_latest_evaluation_result,
    load_golden_set,
    grade_case as grade_retrieval_case,
)

from evaluation.answer_grader import (
    grade_case as grade_answer_case,
)


RESULTS_DIR = Path("evaluation/results")
REPORT_PATH = RESULTS_DIR / "review_report.json"

TOP_K = 3


def get_abstention_result(
    expected_answerable: bool,
    actual_status: str | None,
) -> bool:
    """
    Determine whether abstention behavior is correct.

    Answerable cases should return 'answered'.
    Unanswerable cases should return 'insufficient_evidence'.
    """

    if expected_answerable:
        return actual_status == "answered"

    return actual_status == "insufficient_evidence"


def classify_failure(
    retrieval_result: dict,
    answer_result: dict,
    expected_answerable: bool,
    abstention_pass: bool,
) -> list[str]:
    """Identify relevant failure categories for a case."""

    categories = []

    # Retrieval failure
    if (
        expected_answerable
        and not retrieval_result["hit_at_k"]
    ):
        categories.append("RETRIEVAL_FAILURE")

    # Answerability failure
    if not answer_result["answerability_pass"]:
        categories.append("ANSWERABILITY_FAILURE")

    # Citation and fact checks for answerable cases
    if expected_answerable:

        if not answer_result["citation_presence_pass"]:
            categories.append(
                "CITATION_PRESENCE_FAILURE"
            )

        if not answer_result["citation_validity_pass"]:
            categories.append(
                "CITATION_VALIDITY_FAILURE"
            )

        if not answer_result["required_facts_pass"]:
            categories.append(
                "FACT_COVERAGE_FAILURE"
            )

    # Incorrect abstention behavior
    if not abstention_pass:
        categories.append(
            "ABSTENTION_FAILURE"
        )

    return categories


def get_primary_failure(
    categories: list[str],
) -> str:
    """Select one primary failure category."""

    if not categories:
        return "-"

    priority = [
        "RETRIEVAL_FAILURE",
        "ANSWERABILITY_FAILURE",
        "ABSTENTION_FAILURE",
        "CITATION_PRESENCE_FAILURE",
        "CITATION_VALIDITY_FAILURE",
        "FACT_COVERAGE_FAILURE",
    ]

    for category in priority:
        if category in categories:
            return category

    return categories[0]


def build_review_report() -> dict:
    """Build the complete review report."""

    # Existing evaluation result.
    # No API call is made here.
    evaluation_file, evaluation_cases = (
        load_latest_evaluation_result()
    )

    # Golden set is returned as:
    # {
    #     "GS-001": {...},
    #     "GS-002": {...},
    #     ...
    # }
    golden_set = load_golden_set()

    # Convert evaluation list to dictionary by case ID.
    evaluation_by_id = {
        case["case_id"]: case
        for case in evaluation_cases
    }

    report_cases = []

    for case_id, golden_case in golden_set.items():

        evaluation_case = evaluation_by_id.get(case_id)

        # --------------------------------------------------
        # Missing evaluation result
        # --------------------------------------------------

        if evaluation_case is None:
            report_cases.append(
                {
                    "case_id": case_id,
                    "question": golden_case["question"],
                    "expected_answerable": golden_case.get(
                        "answerable",
                        False,
                    ),
                    "overall_result": "ERROR",
                    "failure_categories": [
                        "MISSING_EVALUATION_RESULT"
                    ],
                    "primary_failure_category": (
                        "MISSING_EVALUATION_RESULT"
                    ),
                }
            )
            continue

        # --------------------------------------------------
        # Actual response
        # --------------------------------------------------

        actual = evaluation_case.get(
            "actual",
            {},
        )

        actual_status = actual.get(
            "status"
        )

        latency_ms = actual.get(
            "latency_ms"
        )

        # --------------------------------------------------
        # Retrieval grading
        # --------------------------------------------------

        retrieval_results = actual.get(
            "retrieval_results",
            {},
        )

        expected_sources = golden_case.get(
            "expected_source_ids",
            [],
        )

        retrieved_sources = retrieval_results.get(
            "source_ids",
            [],
        )

        retrieval_grade = grade_retrieval_case(
            expected_sources=expected_sources,
            retrieved_sources=retrieved_sources,
            top_k=TOP_K,
        )

        # --------------------------------------------------
        # Answer grading
        # --------------------------------------------------

        answer_grade = grade_answer_case(
            golden_case,
            evaluation_case,
        )

        expected_answerable = golden_case.get(
            "answerable",
            False,
        )

        # --------------------------------------------------
        # Abstention
        # --------------------------------------------------

        abstention_pass = get_abstention_result(
            expected_answerable=expected_answerable,
            actual_status=actual_status,
        )

        # --------------------------------------------------
        # Failure classification
        # --------------------------------------------------

        failure_categories = classify_failure(
            retrieval_result=retrieval_grade,
            answer_result=answer_grade,
            expected_answerable=expected_answerable,
            abstention_pass=abstention_pass,
        )

        primary_failure = get_primary_failure(
            failure_categories
        )

        overall_result = (
            "PASS"
            if not failure_categories
            else "FAIL"
        )

        # --------------------------------------------------
        # Combined case report
        # --------------------------------------------------

        report_cases.append(
            {
                "case_id": case_id,
                "question": golden_case["question"],
                "expected_answerable": expected_answerable,
                "actual_status": actual_status,
                "overall_result": overall_result,

                "retrieval": {
                    "expected_source_ids": expected_sources,
                    "retrieved_source_ids": retrieved_sources,
                    "hit_at_3": retrieval_grade[
                        "hit_at_k"
                    ],
                    "recall_at_3": retrieval_grade[
                        "recall_at_k"
                    ],
                    "mrr": retrieval_grade[
                        "reciprocal_rank"
                    ],
                },

                "answer": {
                    "answerability_pass": answer_grade.get(
                        "answerability_pass",
                        False,
                    ),
                    "citation_presence_pass": answer_grade.get(
                        "citation_presence_pass",
                        False,
                    ),
                    "citation_validity_pass": answer_grade.get(
                        "citation_validity_pass",
                        False,
                    ),
                    "required_facts_pass": answer_grade.get(
                        "required_facts_pass",
                        False,
                    ),
                    "abstention_pass": abstention_pass,
                },

                "latency_ms": latency_ms,

                "failure_categories": failure_categories,

                "primary_failure_category": primary_failure,
            }
        )

    # ------------------------------------------------------
    # Overall summary
    # ------------------------------------------------------

    total_cases = len(report_cases)

    passed_cases = sum(
        1
        for case in report_cases
        if case["overall_result"] == "PASS"
    )

    failed_cases = total_cases - passed_cases

    pass_rate = (
        passed_cases / total_cases
        if total_cases
        else 0.0
    )

    return {
        "report_name": (
            "Day 14 Review-Friendly Evaluation Report"
        ),
        "generated_at": datetime.now().isoformat(),
        "source_evaluation_file": str(
            evaluation_file
        ),
        "top_k": TOP_K,

        "summary": {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "pass_rate": pass_rate,
        },

        "cases": report_cases,
    }


def print_review_table(
    report: dict,
) -> None:
    """Print a review-friendly table."""

    print()
    print("=" * 120)
    print(
        "DAY 14 - REVIEW-FRIENDLY EVALUATION REPORT"
    )
    print("=" * 120)

    print(
        f"{'CASE':<10}"
        f"{'RESULT':<9}"
        f"{'RETRIEVAL':<12}"
        f"{'ANSWER':<9}"
        f"{'LATENCY':<12}"
        f"{'FAILURE CATEGORY'}"
    )

    print("-" * 120)

    for case in report["cases"]:

        case_id = case["case_id"]

        overall_result = case[
            "overall_result"
        ]

        retrieval = case.get(
            "retrieval",
            {},
        )

        answer = case.get(
            "answer",
            {},
        )

        # Retrieval result

        retrieval_result = (
            "PASS"
            if retrieval.get(
                "hit_at_3",
                0,
            )
            else "FAIL"
        )

        # Answer result

        answer_checks = [
            answer.get(
                "answerability_pass",
                False,
            ),
            answer.get(
                "citation_presence_pass",
                False,
            ),
            answer.get(
                "citation_validity_pass",
                False,
            ),
            answer.get(
                "required_facts_pass",
                False,
            ),
            answer.get(
                "abstention_pass",
                False,
            ),
        ]

        answer_result = (
            "PASS"
            if all(answer_checks)
            else "FAIL"
        )

        # Latency

        latency = case.get(
            "latency_ms"
        )

        if latency is None:
            latency_text = "-"
        else:
            latency_text = (
                f"{latency:.0f} ms"
            )

        # Failure category

        failure = case.get(
            "primary_failure_category",
            "-",
        )

        print(
            f"{case_id:<10}"
            f"{overall_result:<9}"
            f"{retrieval_result:<12}"
            f"{answer_result:<9}"
            f"{latency_text:<12}"
            f"{failure}"
        )

    print("-" * 120)

    summary = report["summary"]

    print(
        f"Total cases: "
        f"{summary['total_cases']}"
    )

    print(
        f"Passed cases: "
        f"{summary['passed_cases']}"
    )

    print(
        f"Failed cases: "
        f"{summary['failed_cases']}"
    )

    print(
        f"Pass rate: "
        f"{summary['pass_rate']:.2%}"
    )

    print("=" * 120)


def main() -> None:
    """Generate and save the review report."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = build_review_report()

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print_review_table(report)

    print()
    print(
        f"Review report saved to: "
        f"{REPORT_PATH}"
    )


if __name__ == "__main__":
    main()