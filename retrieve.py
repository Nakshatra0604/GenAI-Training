from semantic_search import search_chunks


# Default retrieval configuration

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
    Day 7 retrieval pipeline.

    Accepts a question and returns selected chunks
    with distance and source metadata.
    """

    results = search_chunks(
        question=question,
        top_k=top_k,
        category=category,
        max_distance=max_distance
    )

    return results


def display_results(results):
    """
    Display the raw retrieval results.
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
            f"Distance    : "
            f"{result['distance']}"
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