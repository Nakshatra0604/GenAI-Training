from retrieve import retrieve


def prepare_context(
    results,
    max_context_chunks=3
):
    """
    Prepare retrieved evidence as context for generation.

    Adds stable source labels, removes duplicate chunks,
    and limits the final context to the selected evidence.
    """

    context_parts = []
    seen_chunks = set()

    for result in results:

        chunk_text = result["chunk_text"].strip()

        # Remove duplicate chunks
        if chunk_text in seen_chunks:
            continue

        seen_chunks.add(chunk_text)

        # Create a stable source label
        source_label = (
            f"{result['document_id']}:"
            f"{result['source_path']}"
        )

        context_parts.append(
            f"[Source: {source_label}]\n"
            f"{chunk_text}"
        )

        # Limit final context
        if len(context_parts) >= max_context_chunks:
            break

    return "\n\n".join(context_parts)


if __name__ == "__main__":

    question = input(
        "Enter your question: "
    ).strip()

    if not question:

        print(
            "Question cannot be empty."
        )

    else:

        # Step 1: Retrieve relevant evidence
        results = retrieve(
            question=question
        )

        # Step 2: Prepare the retrieved evidence
        context = prepare_context(
            results
        )

        print("\nFinal Context")
        print("=" * 60)

        if context:
            print(context)
        else:
            print("No relevant context found.")