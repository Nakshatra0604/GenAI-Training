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


def prepare_context(
    results,
    max_context_chunks=3,
    max_distance=0.8
):
    """
    Prepare only evidence chunks that pass
    the configured distance threshold.
    """

    context_parts = []
    seen_chunks = set()

    for result in results:

        if result["distance"] > max_distance:
            continue

        chunk_text = result["chunk_text"].strip()

        if chunk_text in seen_chunks:
            continue

        seen_chunks.add(chunk_text)

        source_label = (
            f"{result['document_id']}:"
            f"{result['source_path']}"
        )

        context_parts.append(
            f"[Source: {source_label}]\n"
            f"{chunk_text}"
        )

        if len(context_parts) >= max_context_chunks:
            break

    return "\n\n".join(context_parts)


def get_selected_results(
    results,
    max_context_chunks=3,
    max_distance=0.8
):
    """
    Return only unique retrieval results that
    pass the evidence threshold.
    """

    selected_results = []
    seen_chunks = set()

    for result in results:

        if result["distance"] > max_distance:
            continue

        chunk_text = result["chunk_text"].strip()

        if chunk_text in seen_chunks:
            continue

        seen_chunks.add(chunk_text)
        selected_results.append(result)

        if len(selected_results) >= max_context_chunks:
            break

    return selected_results


def has_sufficient_evidence(
    results,
    max_distance=0.8
):
    """
    Check whether at least one retrieved chunk
    passes the evidence threshold.
    """

    return any(
        result["distance"] <= max_distance
        for result in results
    )


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


if __name__ == "__main__":

    question = input(
        "Enter your question: "
    ).strip()

    if not question:

        print(
            "Question cannot be empty."
        )

    else:

        # Step 1: Retrieve evidence
        results = retrieve(
            question=question
        )

        # Step 2: Check whether any evidence
        # passes the distance threshold
        if not has_sufficient_evidence(results):

            response = create_abstention_response()

        else:

            # Step 3: Keep only threshold-passing results
            selected_results = get_selected_results(
                results
            )

            # Step 4: Prepare grounded context
            context = prepare_context(
                results
            )

            if not context:

                response = create_abstention_response()

            else:

                # Step 5: Build grounded prompt
                prompt = build_grounded_prompt(
                    question,
                    context
                )

                # Step 6: Generate answer
                answer = generate_answer(
                    prompt
                )

                # Step 7: Validate citations
                citation_result = validate_citations(
                    answer,
                    context
                )

                # Step 8: Decide final status
                if not citation_result["valid"]:

                    # Diagnostic output
                    # This helps us understand why
                    # citation validation failed.
                    print(
                        "\nGenerated Answer Before Abstention"
                    )
                    print("=" * 60)
                    print(answer)

                    print(
                        "\nCitation Validation Result"
                    )
                    print("=" * 60)
                    print(citation_result)

                    response = create_abstention_response()

                else:

                    # Step 9: Build validated response
                    response = AnswerResponse(
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

        # Step 10: Display final response
        print("\nFinal Answer Response")
        print("=" * 60)
        print(
            response.model_dump_json(
                indent=2
            )
        )