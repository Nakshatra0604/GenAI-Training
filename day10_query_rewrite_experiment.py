import json
from pathlib import Path

from query_rewriter import rewrite_query
from semantic_search import search_chunks


WEAK_QUESTIONS_FILE = Path("day9_weak_questions.json")
OUTPUT_FILE = Path("day10_query_rewrite_results.json")

TOP_K = 3


def find_expected_document(case):
    return case["expected_document_id"]


def find_rank(results, expected_document_id):
    for rank, result in enumerate(results, start=1):
        if result["document_id"] == expected_document_id:
            return rank

    return None


def calculate_metrics(results, expected_document_id):
    expected_rank = find_rank(
        results,
        expected_document_id
    )

    if expected_rank is not None:
        reciprocal_rank = 1 / expected_rank
        hit_at_3 = True
    else:
        reciprocal_rank = 0.0
        hit_at_3 = False

    return {
        "retrieved_documents": [
            {
                "rank": rank,
                "document_id": result["document_id"],
                "distance": result["distance"]
            }
            for rank, result in enumerate(results, start=1)
        ],
        "expected_document_rank": expected_rank,
        "hit_at_3": hit_at_3,
        "recall_at_3": 1 if hit_at_3 else 0,
        "reciprocal_rank": reciprocal_rank
    }


# Load Day 9 weak questions
with WEAK_QUESTIONS_FILE.open(
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)


# Only run cases where Day 9 planned query rewriting
query_rewrite_cases = [
    case
    for case in data["weak_questions"]
    if case["case_id"] in ["DQ-001", "DQ-003"]
]


print(
    f"Running query rewriting for "
    f"{len(query_rewrite_cases)} cases"
)


experiment_results = []


for case in query_rewrite_cases:

    case_id = case["case_id"]
    question = case["question"]
    expected_document_id = find_expected_document(case)

    print("\n" + "=" * 60)
    print(f"Case: {case_id}")
    print(f"Original question: {question}")

    # --------------------------------------------------
    # Baseline retrieval
    # --------------------------------------------------

    baseline_results = search_chunks(
        question,
        top_k=TOP_K
    )

    baseline_metrics = calculate_metrics(
        baseline_results,
        expected_document_id
    )

    # --------------------------------------------------
    # Query rewriting
    # --------------------------------------------------

    rewritten_query = rewrite_query(
        question
    )

    print(f"Rewritten query: {rewritten_query}")

    # --------------------------------------------------
    # Retrieval using rewritten query
    # --------------------------------------------------

    rewritten_results = search_chunks(
        rewritten_query,
        top_k=TOP_K
    )

    rewritten_metrics = calculate_metrics(
        rewritten_results,
        expected_document_id
    )

    # --------------------------------------------------
    # Save result
    # --------------------------------------------------

    result = {
        "case_id": case_id,
        "expected_document_id": expected_document_id,

        "baseline": {
            "question": question,
            "top_k": TOP_K,
            **baseline_metrics
        },

        "query_rewrite": {
            "original_question": question,
            "rewritten_query": rewritten_query,
            "top_k": TOP_K,
            **rewritten_metrics
        }
    }

    experiment_results.append(result)

    print("\nBaseline:")
    print(
        [
            result["document_id"]
            for result in baseline_results
        ]
    )

    print(
        f"Expected rank: "
        f"{baseline_metrics['expected_document_rank']}"
    )

    print("\nAfter query rewriting:")
    print(
        [
            result["document_id"]
            for result in rewritten_results
        ]
    )

    print(
        f"Expected rank: "
        f"{rewritten_metrics['expected_document_rank']}"
    )


# Save results
output = {
    "day": 10,
    "task": "Query Rewriting",
    "top_k": TOP_K,
    "cases": experiment_results
}


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        output,
        file,
        indent=2,
        ensure_ascii=False
    )


print("\n" + "=" * 60)
print(
    f"Results saved to {OUTPUT_FILE}"
)