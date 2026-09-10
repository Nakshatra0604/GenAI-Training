import json
from pathlib import Path

from semantic_search import search_chunks
from reranker import rerank_chunks


WEAK_QUESTIONS_FILE = Path("day9_weak_questions.json")
OUTPUT_FILE = Path("day10_reranking_results.json")

CANDIDATE_TOP_K = 5
FINAL_TOP_K = 3


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
        hit_at_3 = expected_rank <= 3
    else:
        reciprocal_rank = 0.0
        hit_at_3 = False

    return {
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


# Reranking is most useful for cases where
# the correct document is retrieved but ranking
# may be improved.
reranking_cases = [
    case
    for case in data["weak_questions"]
    if case["case_id"] in ["DQ-001", "DQ-003", "DQ-005"]
]


print(
    f"Running reranking for "
    f"{len(reranking_cases)} cases"
)


experiment_results = []


for case in reranking_cases:

    case_id = case["case_id"]
    question = case["question"]
    expected_document_id = case["expected_document_id"]

    print("\n" + "=" * 60)
    print(f"Case: {case_id}")
    print(f"Question: {question}")

    # --------------------------------------------------
    # Step 1: Vector retrieval
    # --------------------------------------------------

    candidate_results = search_chunks(
        question,
        top_k=CANDIDATE_TOP_K
    )

    # --------------------------------------------------
    # Step 2: Rerank candidates
    # --------------------------------------------------

    reranked_results = rerank_chunks(
        question,
        candidate_results,
        top_k=FINAL_TOP_K
    )

    # --------------------------------------------------
    # Step 3: Calculate metrics
    # --------------------------------------------------

    baseline_metrics = calculate_metrics(
        candidate_results[:FINAL_TOP_K],
        expected_document_id
    )

    reranked_metrics = calculate_metrics(
        reranked_results,
        expected_document_id
    )

    # --------------------------------------------------
    # Display results
    # --------------------------------------------------

    print("\nOriginal vector retrieval:")

    for rank, result in enumerate(
        candidate_results,
        start=1
    ):
        print(
            f"Rank {rank}: "
            f"{result['document_id']} "
            f"(distance: {result['distance']:.4f})"
        )

    print("\nAfter reranking:")

    for rank, result in enumerate(
        reranked_results,
        start=1
    ):
        print(
            f"Rank {rank}: "
            f"{result['document_id']} "
            f"(rerank score: {result['rerank_score']:.4f}, "
            f"original distance: "
            f"{result['original_distance']:.4f})"
        )

    print("\nExpected document:")
    print(expected_document_id)

    print(
        f"Baseline rank: "
        f"{baseline_metrics['expected_document_rank']}"
    )

    print(
        f"Reranked rank: "
        f"{reranked_metrics['expected_document_rank']}"
    )

    # --------------------------------------------------
    # Save result
    # --------------------------------------------------

    experiment_results.append(
        {
            "case_id": case_id,
            "question": question,
            "expected_document_id": expected_document_id,

            "vector_retrieval": {
                "candidate_top_k": CANDIDATE_TOP_K,
                "selected_top_k": FINAL_TOP_K,
                "results": [
                    {
                        "rank": rank,
                        "document_id": result["document_id"],
                        "original_distance": result["distance"]
                    }
                    for rank, result in enumerate(
                        candidate_results[:FINAL_TOP_K],
                        start=1
                    )
                ],
                **baseline_metrics
            },

            "reranking": {
                "candidate_top_k": CANDIDATE_TOP_K,
                "final_top_k": FINAL_TOP_K,
                "results": [
                    {
                        "rank": rank,
                        "document_id": result["document_id"],
                        "original_distance": result["original_distance"],
                        "rerank_score": result["rerank_score"]
                    }
                    for rank, result in enumerate(
                        reranked_results,
                        start=1
                    )
                ],
                **reranked_metrics
            }
        }
    )


# Save the complete experiment report
output = {
    "day": 10,
    "task": "Cross-Encoder Reranking",
    "candidate_top_k": CANDIDATE_TOP_K,
    "final_top_k": FINAL_TOP_K,
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