from semantic_search import search_chunks


QUESTIONS = [
    {
        "name": "Day 8 answerable",
        "question": "What is the process for requesting software that is not available in the standard IT catalog?",
        "expected_document": "DOC-009"
    },
    {
        "name": "Day 8 unanswerable",
        "question": "What is the company's policy for international business travel?",
        "expected_document": None
    },
    {
        "name": "Day 10 reranking case",
        "question": "What should an employee do if their account is suspected to be compromised?",
        "expected_document": "DOC-007"
    }
]


for case in QUESTIONS:

    print("\n" + "=" * 60)
    print(case["name"])
    print(f"Question: {case['question']}")

    results = search_chunks(
        question=case["question"],
        top_k=5
    )

    for rank, result in enumerate(results, start=1):

        print(
            f"Rank {rank}: "
            f"{result['document_id']} | "
            f"Distance: {result['distance']:.4f}"
        )

        if result["document_id"] == case["expected_document"]:
            print("       <-- Expected document")

        if result["distance"] <= 0.8:
            print("       <-- Passes Day 8 threshold")