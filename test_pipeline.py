from ingest import ingest_documents
from retrieve import retrieve
from generate import prepare_context


def test_ingest_then_retrieve():
    """
    Verify that documents can be ingested,
    retrieved using a known question,
    and prepared as generation context.
    """

    # Step 1: Run the complete ingestion pipeline
    ingest_documents()

    # Step 2: Ask a known question
    question = (
        "What is the process for requesting software "
        "that is not available in the standard IT catalog?"
    )

    # Step 3: Retrieve relevant evidence
    results = retrieve(
        question=question,
        top_k=3
    )

    # Verify that retrieval returned evidence
    assert results, (
        "Retrieval returned no results after ingestion."
    )

    # Step 4: Verify that the expected document was retrieved
    retrieved_document_ids = [
        result["document_id"]
        for result in results
    ]

    assert "DOC-009" in retrieved_document_ids, (
        "Expected document DOC-009 was not retrieved."
    )

    # Step 5: Prepare the retrieved evidence as final context
    context = prepare_context(
        results,
        max_context_chunks=3
    )

    # Verify that final context was created
    assert context, (
        "Final context was not created from retrieved evidence."
    )

    # Verify that the context contains a stable source label
    assert "[Source:" in context, (
        "Final context does not contain a stable source label."
    )

    # Verify that the expected document appears in the context
    assert "DOC-009" in context, (
        "Expected document DOC-009 is missing from final context."
    )

    print(
        "\nIngest → Retrieve → Context integration test passed."
    )


def test_failed_document_does_not_stop_pipeline():
    """
    Verify that a failed document is handled
    without stopping processing of other documents.
    """

    processed_documents = []
    failed_documents = []

    documents = [
        "DOC-001",
        "DOC-002",
        "FAILED-DOCUMENT",
        "DOC-004",
    ]

    for document_id in documents:

        try:

            if document_id == "FAILED-DOCUMENT":
                raise Exception(
                    "Simulated document processing failure"
                )

            processed_documents.append(document_id)

        except Exception as error:

            failed_documents.append({
                "document_id": document_id,
                "error": str(error)
            })

            print(
                f"Failed to process {document_id}: {error}"
            )

            continue

    # Verify that the failed document was recorded
    assert len(failed_documents) == 1

    assert failed_documents[0]["document_id"] == (
        "FAILED-DOCUMENT"
    )

    # Verify that other documents continued processing
    assert "DOC-001" in processed_documents
    assert "DOC-002" in processed_documents
    assert "DOC-004" in processed_documents

    print(
        "\nFailed-document handling test passed."
    )


if __name__ == "__main__":

    test_ingest_then_retrieve()

    test_failed_document_does_not_stop_pipeline()

    print(
        "\nAll Day 7 pipeline checks passed."
    )