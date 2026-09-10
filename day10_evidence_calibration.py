from semantic_search import search_chunks
from reranker import rerank_chunks


QUESTIONS = [
    {
        "name": "Known answerable",
        "question": "What is the process for requesting software that is not available in the standard IT catalog?"
    },
    {
        "name": "Known unanswerable",
        "question": "What is the company's policy for international business travel?"
    },
    {
        "name": "Compromised account",
        "question": "What should an employee do if their account is suspected to be compromised?"
    }
]


for case in QUESTIONS:

    print("\n" + "=" * 70)
    print(case["name"])
    print(f"Question: {case['question']}")

    candidates = search_chunks(
        question=case["question"],
        top_k=5
    )

    results = rerank_chunks(
        question=case["question"],
        retrieved_chunks=candidates,
        top_k=3
    )

    print("\nFinal reranked results:")

    for rank, result in enumerate(results, start=1):

        print(
            f"Rank {rank}: "
            f"{result['document_id']} | "
            f"Vector distance: {result['original_distance']:.4f} | "
            f"Rerank score: {result['rerank_score']:.4f}"
        )