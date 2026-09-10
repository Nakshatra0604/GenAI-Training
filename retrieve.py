from semantic_search import search_chunks
from reranker import rerank_chunks


# Final retrieval configuration
CANDIDATE_TOP_K = 5
DEFAULT_TOP_K = 3
DEFAULT_CATEGORY = None
DEFAULT_MAX_DISTANCE = None


def retrieve(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    category: str | None = DEFAULT_CATEGORY,
    max_distance: float | None = DEFAULT_MAX_DISTANCE
):
    """
    Day 10 retrieval pipeline.

    1. Retrieve candidate chunks using vector search.
    2. Rerank the candidates using the cross-encoder.
    3. Return the final top-k chunks.
    """

    candidate_results = search_chunks(
        question=question,
        top_k=max(CANDIDATE_TOP_K, top_k),
        category=category,
        max_distance=max_distance
    )

    reranked_results = rerank_chunks(
        question=question,
        retrieved_chunks=candidate_results,
        top_k=top_k
    )

    return reranked_results


def display_results(results):
    """
    Display the final reranked retrieval results.
    """

    if not results:
        print("\nNo relevant evidence found.")
        return

    print("\nRetrieved Evidence")
    print("=" * 60)

    for index, result in enumerate(results, start=1):

        print(f"\n[Result {index}]")

        print(
            f"Document ID : "
            f"{result['document_id']}"
        )

        print(
            f"Title       : "
            f"{result['title']}"
        )

        print(
            f"Source      : "
            f"{result['source_path']}"
        )

        print(
            f"Vector Distance : "
            f"{result['distance']}"
        )

        print(
            f"Rerank Score    : "
            f"{result['rerank_score']}"
        )

        print(
            f"Chunk       :\n"
            f"{result['chunk_text']}"
        )

        print("-" * 60)


if __name__ == "__main__":

    question = input(
        "Enter your question: "
    ).strip()

    if not question:

        print(
            "Question cannot be empty."
        )

    else:

        results = retrieve(
            question=question
        )

        display_results(results)