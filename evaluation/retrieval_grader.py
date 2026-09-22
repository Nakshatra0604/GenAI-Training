import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

GOLDEN_SET_PATH = PROJECT_ROOT / "evaluation" / "golden_set.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file into a list of dictionaries."""
    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def calculate_hit_at_k(
    expected_sources: list[str],
    retrieved_sources: list[str],
) -> int:
    """
    Hit@K is 1 when at least one expected source
    appears in the retrieved Top-K results.
    Otherwise it is 0.
    """
    expected = set(expected_sources)
    retrieved = set(retrieved_sources)

    return int(bool(expected & retrieved))


def calculate_recall_at_k(
    expected_sources: list[str],
    retrieved_sources: list[str],
) -> float:
    """
    Recall@K measures how many expected sources were
    retrieved within Top-K.

    Recall@K =
        expected sources retrieved / total expected sources
    """
    if not expected_sources:
        return 0.0

    expected = set(expected_sources)
    retrieved = set(retrieved_sources)

    matched_sources = expected & retrieved

    return len(matched_sources) / len(expected)


def calculate_reciprocal_rank(
    expected_sources: list[str],
    retrieved_sources: list[str],
) -> float:
    """
    Calculate Reciprocal Rank for one evaluation case.

    If the first expected source appears at rank 1:
        RR = 1.0

    If it appears at rank 2:
        RR = 0.5

    If it appears at rank 3:
        RR = 0.3333

    If no expected source is retrieved:
        RR = 0.0
    """
    expected = set(expected_sources)

    for rank, source_id in enumerate(retrieved_sources, start=1):
        if source_id in expected:
            return 1.0 / rank

    return 0.0


def calculate_mrr(reciprocal_ranks: list[float]) -> float:
    """Calculate Mean Reciprocal Rank across all evaluated cases."""
    if not reciprocal_ranks:
        return 0.0

    return sum(reciprocal_ranks) / len(reciprocal_ranks)


def grade_case(
    expected_sources: list[str],
    retrieved_sources: list[str],
    top_k: int = 3,
) -> dict:
    """
    Grade retrieval performance for one answerable evaluation case.

    The evaluation result already contains document/source IDs,
    so no chunk-text-to-document mapping is required.
    """
    retrieved_top_k = retrieved_sources[:top_k]

    hit_at_k = calculate_hit_at_k(
        expected_sources=expected_sources,
        retrieved_sources=retrieved_top_k,
    )

    recall_at_k = calculate_recall_at_k(
        expected_sources=expected_sources,
        retrieved_sources=retrieved_top_k,
    )

    reciprocal_rank = calculate_reciprocal_rank(
        expected_sources=expected_sources,
        retrieved_sources=retrieved_top_k,
    )

    return {
        "expected_sources": expected_sources,
        "retrieved_sources": retrieved_top_k,
        "hit_at_k": hit_at_k,
        "recall_at_k": recall_at_k,
        "reciprocal_rank": reciprocal_rank,
    }


def grade_evaluation_run(
    evaluation_results: list[dict],
    golden_cases: dict[str, dict],
    top_k: int = 3,
) -> dict:
    """
    Grade retrieval performance for an entire evaluation run.

    Only answerable golden cases are included in retrieval metrics.

    Unanswerable cases are intentionally excluded because their
    retrieval expectation is not a successful source retrieval.
    Those cases will be evaluated separately by the answer grader
    for correct abstention.
    """
    case_results = []
    reciprocal_ranks = []

    excluded_cases = []

    for result in evaluation_results:
        case_id = result["case_id"]

        golden_case = golden_cases.get(case_id)

        if not golden_case:
            continue

        answerable = golden_case.get("answerable", False)

        if not answerable:
            excluded_cases.append(case_id)
            continue

        expected_sources = golden_case.get("expected_source_ids", [])

        actual = result.get("actual", {})
        retrieval_results = actual.get("retrieval_results", {})

        retrieved_sources = retrieval_results.get("source_ids", [])

        case_grade = grade_case(
            expected_sources=expected_sources,
            retrieved_sources=retrieved_sources,
            top_k=top_k,
        )

        case_results.append(
            {
                "case_id": case_id,
                **case_grade,
            }
        )

        reciprocal_ranks.append(
            case_grade["reciprocal_rank"]
        )

    total_cases = len(case_results)

    if total_cases == 0:
        return {
            "top_k": top_k,
            "total_cases": 0,
            "excluded_unanswerable_cases": len(excluded_cases),
            "excluded_case_ids": excluded_cases,
            "hit_rate_at_k": 0.0,
            "recall_at_k": 0.0,
            "mrr": 0.0,
            "cases": [],
        }

    hit_rate = sum(
        case["hit_at_k"]
        for case in case_results
    ) / total_cases

    recall = sum(
        case["recall_at_k"]
        for case in case_results
    ) / total_cases

    mrr = calculate_mrr(reciprocal_ranks)

    return {
        "top_k": top_k,
        "total_cases": total_cases,
        "excluded_unanswerable_cases": len(excluded_cases),
        "excluded_case_ids": excluded_cases,
        "hit_rate_at_k": hit_rate,
        "recall_at_k": recall,
        "mrr": mrr,
        "cases": case_results,
    }


def load_latest_evaluation_result() -> tuple[Path, list[dict]]:
    """
    Load the most recent saved evaluation result.
    """
    results_dir = PROJECT_ROOT / "evaluation" / "results"

    result_files = sorted(
        results_dir.glob("evaluation_run_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not result_files:
        raise FileNotFoundError(
            "No evaluation result files were found in evaluation/results."
        )

    latest_file = result_files[0]

    with latest_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return latest_file, data["results"]


def load_golden_set() -> dict[str, dict]:
    """Load the golden dataset indexed by case ID."""
    golden_records = load_jsonl(GOLDEN_SET_PATH)

    return {
        record["case_id"]: record
        for record in golden_records
    }


def main():
    print("=" * 70)
    print("DAY 14 - RETRIEVAL GRADER")
    print("=" * 70)

    evaluation_file, evaluation_results = load_latest_evaluation_result()
    golden_cases = load_golden_set()

    print(f"Evaluation run: {evaluation_file.name}")
    print(f"Total evaluation cases: {len(evaluation_results)}")
    print()

    scorecard = grade_evaluation_run(
        evaluation_results=evaluation_results,
        golden_cases=golden_cases,
        top_k=3,
    )

    print("-" * 70)
    print("RETRIEVAL SCORECARD")
    print("-" * 70)

    print(f"Top-K:                         {scorecard['top_k']}")
    print(f"Evaluated answerable cases:    {scorecard['total_cases']}")
    print(
        f"Excluded unanswerable cases:  "
        f"{scorecard['excluded_unanswerable_cases']}"
    )

    print(
        f"Hit@3:                         "
        f"{scorecard['hit_rate_at_k']:.4f} "
        f"({scorecard['hit_rate_at_k'] * 100:.2f}%)"
    )

    print(
        f"Recall@3:                      "
        f"{scorecard['recall_at_k']:.4f} "
        f"({scorecard['recall_at_k'] * 100:.2f}%)"
    )

    print(
        f"MRR:                           "
        f"{scorecard['mrr']:.4f}"
    )

    print()
    print(
        f"Excluded case IDs: "
        f"{scorecard['excluded_case_ids']}"
    )

    print()
    print("-" * 70)
    print("PER-CASE RETRIEVAL RESULTS")
    print("-" * 70)

    for case in scorecard["cases"]:
        print(
            f"{case['case_id']} | "
            f"Expected: {case['expected_sources']} | "
            f"Retrieved: {case['retrieved_sources']} | "
            f"Hit@3: {case['hit_at_k']} | "
            f"Recall@3: {case['recall_at_k']:.2f} | "
            f"RR: {case['reciprocal_rank']:.2f}"
        )


if __name__ == "__main__":
    main()