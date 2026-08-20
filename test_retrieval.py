import json
from pathlib import Path

from semantic_search import search_chunks

TEST_FILE = Path("retrieval_test_set.json")

with TEST_FILE.open("r", encoding = "utf-8") as file:
    test_cases = json.load(file)

print(f"Loaded {len(test_cases)} retrieval test cases")

results_report = []

for case in test_cases:
    question = case["question"]
    expected_document_id = case["expected_document_id"]

    results = search_chunks(
        question,
        top_k=3
    )

    retrieved_document_ids = [
        result["document_id"]
        for result in results
    ]

    passed = expected_document_id in retrieved_document_ids

    test_result = {
        "question": question,
        "expected_document_id": expected_document_id,
        "results": results,
        "expected_document_found_in_top_3": passed
    }

    results_report.append(test_result)

    print("\n" + "-" * 60)
    print(f"Question: {question}")
    print(f"Expected document: {expected_document_id}")
    print(f"Retrieved documents: {retrieved_document_ids}")
    print(f"Result: {'PASS' if passed else 'FAIL'}")


with open(
    "retrieval_results.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        results_report,
        file,
        indent=2,
        ensure_ascii=False
    )

print("\nRetrieval result report saved to retrieval_results.json")