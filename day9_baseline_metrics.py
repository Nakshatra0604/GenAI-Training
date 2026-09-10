import json
from pathlib import Path

from semantic_search import search_chunks


TEST_FILE = Path("day9_weak_questions.json")
OUTPUT_FILE = Path("day9_baseline_metrics.json")

TOP_K = 3


# Load the five Day 9 weak questions
with TEST_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)

weak_questions = data["weak_questions"]

print(f"Loaded {len(weak_questions)} Day 9 test cases")


per_question_results = []

total_hits = 0
total_reciprocal_rank = 0.0


for case in weak_questions:
    case_id = case["case_id"]
    question = case["question"]
    expected_document_id = case["expected_document_id"]

    # Run retrieval using the frozen baseline top-k value
    results = search_chunks(
        question,
        top_k=TOP_K
    )

    retrieved_document_ids = [
        result["document_id"]
        for result in results
    ]

    # Find the rank of the expected document
    expected_rank = None

    for rank, document_id in enumerate(
        retrieved_document_ids,
        start=1
    ):
        if document_id == expected_document_id:
            expected_rank = rank
            break

    # Hit@3 / Recall@3
    hit_at_k = expected_rank is not None
    recall_at_k = 1 if hit_at_k else 0

    # Reciprocal Rank
    if expected_rank is not None:
        reciprocal_rank = 1 / expected_rank
    else:
        reciprocal_rank = 0.0

    if hit_at_k:
        total_hits += 1

    total_reciprocal_rank += reciprocal_rank

    question_result = {
        "case_id": case_id,
        "question": question,
        "expected_document_id": expected_document_id,
        "retrieved_documents": [
            {
                "rank": rank,
                "document_id": result["document_id"],
                "distance": result["distance"]
            }
            for rank, result in enumerate(results, start=1)
        ],
        "expected_document_rank": expected_rank,
        "hit_at_3": hit_at_k,
        "recall_at_3": recall_at_k,
        "reciprocal_rank": reciprocal_rank
    }

    per_question_results.append(question_result)

    print("\n" + "-" * 60)
    print(f"Case: {case_id}")
    print(f"Question: {question}")
    print(f"Expected document: {expected_document_id}")
    print(f"Retrieved documents: {retrieved_document_ids}")
    print(f"Expected document rank: {expected_rank}")
    print(f"Hit@3: {hit_at_k}")
    print(f"Recall@3: {recall_at_k}")
    print(f"Reciprocal Rank: {reciprocal_rank:.3f}")


# Calculate overall metrics
total_cases = len(weak_questions)

hit_rate = total_hits / total_cases if total_cases else 0.0
recall_at_3 = total_hits / total_cases if total_cases else 0.0
mrr = (
    total_reciprocal_rank / total_cases
    if total_cases
    else 0.0
)


# Build final Day 9 metric report
metrics_report = {
    "day": 9,
    "task": "Baseline Retrieval Metrics",
    "baseline_config_file": "baseline_config.yaml",
    "test_file": "day9_weak_questions.json",
    "top_k": TOP_K,
    "per_question_results": per_question_results,
    "overall_metrics": {
        "total_questions": total_cases,
        "hit_rate": hit_rate,
        "recall_at_3": recall_at_3,
        "mrr": mrr
    }
}


# Save report
with OUTPUT_FILE.open(
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        metrics_report,
        file,
        indent=2,
        ensure_ascii=False
    )


print("\n" + "=" * 60)
print("Overall Baseline Metrics")
print("=" * 60)
print(f"Hit Rate:   {hit_rate:.3f}")
print(f"Recall@3:   {recall_at_3:.3f}")
print(f"MRR:        {mrr:.3f}")

print(
    f"\nDay 9 baseline metrics saved to {OUTPUT_FILE}"
)