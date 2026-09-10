import json
import time
from pathlib import Path

from semantic_search import search_chunks
from reranker import rerank_chunks


TEST_SET_FILE = Path("retrieval_test_set.json")
OUTPUT_FILE = Path("day10_regression_results.json")

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

    hit_at_3 = (
        expected_rank is not None
        and expected_rank <= FINAL_TOP_K
    )

    if expected_rank is not None:
        reciprocal_rank = 1 / expected_rank
    else:
        reciprocal_rank = 0.0

    return {
        "expected_document_rank": expected_rank,
        "hit_at_3": hit_at_3,
        "recall_at_3": 1 if hit_at_3 else 0,
        "reciprocal_rank": reciprocal_rank
    }


# Load the Day 6 regression test set
with TEST_SET_FILE.open(
    "r",
    encoding="utf-8"
) as file:
    test_cases = json.load(file)


print(
    f"Running regression test for "
    f"{len(test_cases)} questions"
)


# --------------------------------------------------
# Warm-up
# --------------------------------------------------
# The first model/API call can include one-time
# initialization overhead. We warm up both retrieval
# and reranking before measuring actual latency.
# --------------------------------------------------

print("\nWarming up retrieval and reranker...")

warmup_question = test_cases[0]["question"]

warmup_candidates = search_chunks(
    warmup_question,
    top_k=CANDIDATE_TOP_K
)

rerank_chunks(
    warmup_question,
    warmup_candidates,
    top_k=FINAL_TOP_K
)

print("Warm-up complete.")


results = []


for index, case in enumerate(
    test_cases,
    start=1
):

    question = case["question"]
    expected_document_id = case["expected_document_id"]

    print("\n" + "=" * 60)
    print(f"Question {index}")
    print(f"Question: {question}")
    print(f"Expected document: {expected_document_id}")

    # --------------------------------------------------
    # Baseline: original vector retrieval
    # --------------------------------------------------

    baseline_start = time.perf_counter()

    baseline_results = search_chunks(
        question,
        top_k=FINAL_TOP_K
    )

    baseline_end = time.perf_counter()

    baseline_latency = (
        baseline_end - baseline_start
    )

    baseline_metrics = calculate_metrics(
        baseline_results,
        expected_document_id
    )

    # --------------------------------------------------
    # Improved configuration:
    # Vector retrieval + cross-encoder reranking
    # --------------------------------------------------

    reranking_start = time.perf_counter()

    candidate_results = search_chunks(
        question,
        top_k=CANDIDATE_TOP_K
    )

    reranked_results = rerank_chunks(
        question,
        candidate_results,
        top_k=FINAL_TOP_K
    )

    reranking_end = time.perf_counter()

    reranking_latency = (
        reranking_end - reranking_start
    )

    additional_latency = (
        reranking_latency - baseline_latency
    )

    reranked_metrics = calculate_metrics(
        reranked_results,
        expected_document_id
    )

    # --------------------------------------------------
    # Display comparison
    # --------------------------------------------------

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

    print(
        f"Latency: "
        f"{baseline_latency:.4f} seconds"
    )

    print("\nAfter reranking:")

    for rank, result in enumerate(
        reranked_results,
        start=1
    ):
        print(
            f"Rank {rank}: "
            f"{result['document_id']} "
            f"(rerank score: "
            f"{result['rerank_score']:.4f})"
        )

    print(
        f"Expected rank: "
        f"{reranked_metrics['expected_document_rank']}"
    )

    print(
        f"Latency: "
        f"{reranking_latency:.4f} seconds"
    )

    print(
        f"Additional latency: "
        f"{additional_latency:.4f} seconds"
    )

    # --------------------------------------------------
    # Save per-question result
    # --------------------------------------------------

    results.append(
        {
            "question": question,
            "expected_document_id": expected_document_id,

            "baseline": {
                "top_k": FINAL_TOP_K,
                "latency_seconds": baseline_latency,

                "retrieved_documents": [
                    {
                        "rank": rank,
                        "document_id": result["document_id"],
                        "distance": result["distance"]
                    }
                    for rank, result in enumerate(
                        baseline_results,
                        start=1
                    )
                ],

                **baseline_metrics
            },

            "reranking": {
                "candidate_top_k": CANDIDATE_TOP_K,
                "final_top_k": FINAL_TOP_K,
                "latency_seconds": reranking_latency,
                "additional_latency_seconds": (
                    additional_latency
                ),

                "retrieved_documents": [
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


# --------------------------------------------------
# Calculate aggregate retrieval metrics
# --------------------------------------------------

baseline_hit_rate = sum(
    result["baseline"]["hit_at_3"]
    for result in results
) / len(results)

baseline_recall = sum(
    result["baseline"]["recall_at_3"]
    for result in results
) / len(results)

baseline_mrr = sum(
    result["baseline"]["reciprocal_rank"]
    for result in results
) / len(results)


reranking_hit_rate = sum(
    result["reranking"]["hit_at_3"]
    for result in results
) / len(results)

reranking_recall = sum(
    result["reranking"]["recall_at_3"]
    for result in results
) / len(results)

reranking_mrr = sum(
    result["reranking"]["reciprocal_rank"]
    for result in results
) / len(results)


# --------------------------------------------------
# Calculate aggregate latency
# --------------------------------------------------

baseline_average_latency = sum(
    result["baseline"]["latency_seconds"]
    for result in results
) / len(results)

reranking_average_latency = sum(
    result["reranking"]["latency_seconds"]
    for result in results
) / len(results)

average_additional_latency = (
    reranking_average_latency
    - baseline_average_latency
)


# --------------------------------------------------
# Save complete regression report
# --------------------------------------------------

output = {
    "day": 10,
    "task": "Regression Testing",
    "test_set_file": str(TEST_SET_FILE),

    "baseline_configuration": {
        "retrieval": "vector_search",
        "top_k": FINAL_TOP_K
    },

    "reranking_configuration": {
        "retrieval": "vector_search",
        "candidate_top_k": CANDIDATE_TOP_K,
        "final_top_k": FINAL_TOP_K,
        "reranker": "cross-encoder"
    },

    "aggregate_metrics": {
        "baseline": {
            "hit_rate_at_3": baseline_hit_rate,
            "recall_at_3": baseline_recall,
            "mrr": baseline_mrr
        },

        "reranking": {
            "hit_rate_at_3": reranking_hit_rate,
            "recall_at_3": reranking_recall,
            "mrr": reranking_mrr
        }
    },

    "latency": {
        "baseline_average_seconds": (
            baseline_average_latency
        ),
        "reranking_average_seconds": (
            reranking_average_latency
        ),
        "average_additional_seconds": (
            average_additional_latency
        )
    },

    "questions": results
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


# --------------------------------------------------
# Print aggregate comparison
# --------------------------------------------------

print("\n" + "=" * 60)
print("REGRESSION SUMMARY")

print("\nBaseline:")
print(
    f"  Hit Rate@3: "
    f"{baseline_hit_rate:.3f}"
)
print(
    f"  Recall@3: "
    f"{baseline_recall:.3f}"
)
print(
    f"  MRR: "
    f"{baseline_mrr:.3f}"
)
print(
    f"  Average latency: "
    f"{baseline_average_latency:.4f} seconds"
)

print("\nAfter reranking:")
print(
    f"  Hit Rate@3: "
    f"{reranking_hit_rate:.3f}"
)
print(
    f"  Recall@3: "
    f"{reranking_recall:.3f}"
)
print(
    f"  MRR: "
    f"{reranking_mrr:.3f}"
)
print(
    f"  Average latency: "
    f"{reranking_average_latency:.4f} seconds"
)

print(
    f"\nAverage additional latency: "
    f"{average_additional_latency:.4f} seconds"
)

print("\n" + "=" * 60)
print(
    f"Regression results saved to {OUTPUT_FILE}"
)