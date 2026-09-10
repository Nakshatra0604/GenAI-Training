import os

from dotenv import load_dotenv
from openai import OpenAI

from retrieve import retrieve
from grounded_prompt import build_grounded_prompt
from citation_validator import validate_citations
from answer_model import AnswerResponse


load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
GENERATION_MODEL = os.getenv("GENERATION_MODEL")


client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


MAX_CONTEXT_CHUNKS = 3


def prepare_context(
    results
):
    """
    Convert selected retrieval results
    into grounded LLM context.
    """

    context_parts = []

    for result in results:

        source = (
            f"{result['document_id']}:"
            f"{result['source_path']}"
        )

        chunk_text = result["chunk_text"]

        context_parts.append(
            f"[Source: {source}]\n"
            f"{chunk_text}"
        )

    return "\n\n".join(context_parts)


def get_selected_results(
    results,
    max_context_chunks=MAX_CONTEXT_CHUNKS
):
    """
    Return unique final reranked results.
    """

    selected_results = []
    seen_chunks = set()

    for result in results:

        chunk_text = result["chunk_text"].strip()

        if chunk_text in seen_chunks:
            continue

        seen_chunks.add(chunk_text)

        selected_results.append(result)

        if len(selected_results) >= max_context_chunks:
            break

    return selected_results


def has_sufficient_evidence(results):
    """
    Check whether the reranker identified at least one
    strongly relevant candidate.

    The cross-encoder score is used because the selected
    Day 10 retrieval configuration is based on reranking.
    """

    if not results:
        return False

    return results[0]["rerank_score"] > 0


def generate_answer(prompt):
    """
    Generate an answer using the configured generation model.
    """

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def create_abstention_response():
    """
    Create the standard abstention response.
    """

    return AnswerResponse(
        answer=(
            "Insufficient evidence to answer "
            "the question from the provided documents."
        ),
        sources=[],
        chunks=[],
        scores=[],
        status="insufficient_evidence"
    )


def answer_question(
    question: str,
    category: str | None = None,
    max_distance: float | None = None
) -> AnswerResponse:
    """
    Run the complete grounded RAG question-answering pipeline.

    Pipeline:
    retrieval -> reranking -> evidence check ->
    grounded prompt -> generation -> citation validation.
    """

    # Step 1: Retrieve final reranked evidence.
    #
    # retrieve.py performs:
    # vector search -> 5 candidates
    # -> cross-encoder reranking -> final top 3
    results = retrieve(
        question=question,
        category=category,
        max_distance=max_distance
    )

    # Step 2: Check whether the reranker
    # identifies sufficient evidence.
    if not has_sufficient_evidence(results):

        return create_abstention_response()

    # Step 3: Select the final reranked chunks.
    selected_results = get_selected_results(
        results
    )

    # Step 4: Prepare grounded context.
    context = prepare_context(
        selected_results
    )

    if not context:

        return create_abstention_response()

    # Step 5: Build grounded prompt.
    prompt = build_grounded_prompt(
        question,
        context
    )

    # Step 6: Generate answer.
    answer = generate_answer(
        prompt
    )

    # Step 7: Validate citations.
    citation_result = validate_citations(
        answer,
        context
    )

    # Step 8: Decide final status.
    if not citation_result["valid"]:

        return create_abstention_response()

    return AnswerResponse(
        answer=answer,
        sources=citation_result[
            "valid_sources"
        ],
        chunks=[
            result["chunk_text"]
            for result in selected_results
        ],
        scores=[
            result["distance"]
            for result in selected_results
        ],
        status="answered"
    )


if __name__ == "__main__":

    question = input(
        "Enter your question: "
    ).strip()

    if not question:

        print(
            create_abstention_response().model_dump_json(
                indent=2
            )
        )

    else:

        response = answer_question(
            question
        )

        print("\nFinal Answer Response")
        print("=" * 60)
        print(
            response.model_dump_json(
                indent=2
            )
        )