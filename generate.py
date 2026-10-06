import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from retrieve import retrieve
from grounded_prompt import build_grounded_prompt, SYSTEM_RULES
from citation_validator import validate_citations
from answer_model import AnswerResponse
from api.errors import ProviderError
from content_guardrail import check_content_policy


load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
GENERATION_MODEL = os.getenv("GENERATION_MODEL")


client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


MAX_CONTEXT_CHUNKS = 3


def prepare_context(results):
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
    Check whether retrieved results contain
    the minimum required evidence fields.
    """

    if not results:
        return False

    for result in results:
        document_id = result.get("document_id")
        source_path = result.get("source_path")
        chunk_text = result.get("chunk_text")
        rerank_score = result.get("rerank_score")

        if not document_id:
            return False

        if not source_path:
            return False

        if not isinstance(
            chunk_text,
            str
        ) or not chunk_text.strip():
            return False

        if not isinstance(
            rerank_score,
            (int, float)
        ):
            return False

    return True


def generate_answer(prompt):
    """
    Generate an answer using the configured generation model.
    """

    try:
        response = client.chat.completions.create(
            model=GENERATION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_RULES
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000
        )

        return response.choices[0].message.content

    except Exception as exc:
        raise ProviderError(
            "The AI provider failed to generate a response."
        ) from exc


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
        retrieved_source_ids=[],
        status="insufficient_evidence"
    )


def validate_final_response(
    response,
    selected_results
):
    """
    Validate the final AnswerResponse before returning it.

    Ensures:
    - The response matches the AnswerResponse schema.
    - The answer is not empty.
    - The status is allowed.
    - Required fields are populated for answered responses.
    - Abstention responses do not contain partial evidence.
    - Sources belong to the selected retrieved evidence.
    - Retrieved document IDs belong to the selected evidence.
    - Scores contain valid numeric values.
    """

    try:
        validated = AnswerResponse.model_validate(
            response.model_dump()
        )
    except Exception:
        return None

    if not validated.answer.strip():
        return None

    if validated.status == "insufficient_evidence":
        if (
            validated.sources
            or validated.chunks
            or validated.scores
            or validated.retrieved_source_ids
        ):
            return None

        return validated

    if validated.status != "answered":
        return None

    if not validated.sources:
        return None

    if not validated.chunks:
        return None

    if not validated.scores:
        return None

    if not validated.retrieved_source_ids:
        return None

    if not all(
        isinstance(
            score,
            (int, float)
        )
        for score in validated.scores
    ):
        return None

    expected_sources = {
        f"{result['document_id']}:{result['source_path']}"
        for result in selected_results
    }

    if not set(
        validated.sources
    ).issubset(
        expected_sources
    ):
        return None

    expected_document_ids = {
        result["document_id"]
        for result in selected_results
    }

    if not set(
        validated.retrieved_source_ids
    ).issubset(
        expected_document_ids
    ):
        return None

    return validated


def answer_question(
    question: str,
    category: str | None = None,
    max_distance: float | None = None,
    timing: dict | None = None
) -> AnswerResponse:
    """
    Run the complete grounded RAG question-answering pipeline.

    Pipeline:
    content policy -> retrieval -> reranking ->
    evidence check -> grounded prompt -> generation ->
    citation validation -> final response validation.

    Optional timing output records:
    - retrieval_latency_ms
    - generation_latency_ms
    """

    if timing is None:
        timing = {}

    # Step 0: Check content and policy rules.
    policy_result = check_content_policy(
        question
    )

    if not policy_result["allowed"]:
        return create_abstention_response()

    # Step 1: Retrieve final reranked evidence.
    #
    # retrieve.py performs:
    # vector search -> 5 candidates
    # -> cross-encoder reranking -> final top 3

    retrieval_started = time.perf_counter()

    results = retrieve(
        question=question,
        category=category,
        max_distance=max_distance
    )

    timing["retrieval_latency_ms"] = (
        time.perf_counter() - retrieval_started
    ) * 1000

    # Step 2: Check whether the retrieved
    # results contain sufficient evidence.
    if not has_sufficient_evidence(
        results
    ):
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

    # Step 5: Build grounded user prompt.
    prompt = build_grounded_prompt(
        question,
        context
    )

    # Step 6: Generate answer.
    generation_started = time.perf_counter()

    answer = generate_answer(
        prompt
    )

    timing["generation_latency_ms"] = (
        time.perf_counter() - generation_started
    ) * 1000

    # Step 7: Validate citations.
    citation_result = validate_citations(
        answer,
        context
    )

    # Step 8: Reject invalid citations.
    if not citation_result["valid"]:
        return create_abstention_response()

    # Step 9: Build the structured final response.
    response = AnswerResponse(
        answer=answer,
        sources=citation_result["valid_sources"],
        chunks=[
            result["chunk_text"]
            for result in selected_results
        ],
        scores=[
            result["distance"]
            for result in selected_results
        ],
        retrieved_source_ids=[
            result["document_id"]
            for result in selected_results
        ],
        status="answered"
    )

    # Step 10: Validate the complete response.
    validated_response = validate_final_response(
        response,
        selected_results
    )

    # Do not return partially valid output.
    if validated_response is None:
        return create_abstention_response()

    return validated_response


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

        timing = {}

        response = answer_question(
            question,
            timing=timing
        )

        print("\nFinal Answer Response")
        print("=" * 60)

        print(
            response.model_dump_json(
                indent=2
            )
        )

        print("\nLatency")
        print("=" * 60)

        print(
            "Retrieval latency:",
            round(
                timing.get(
                    "retrieval_latency_ms",
                    0
                ),
                2
            ),
            "ms"
        )

        print(
            "Generation latency:",
            round(
                timing.get(
                    "generation_latency_ms",
                    0
                ),
                2
            ),
            "ms"
        )