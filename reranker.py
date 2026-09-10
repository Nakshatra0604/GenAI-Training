import os

from dotenv import load_dotenv
from sentence_transformers import CrossEncoder


load_dotenv()

RERANKER_MODEL = os.getenv("RERANKER_MODEL")

reranker = CrossEncoder(
    RERANKER_MODEL
)


def rerank_chunks(
    question,
    retrieved_chunks,
    top_k=3
):
    if not retrieved_chunks:
        return []

    pairs = [
        [question, chunk["chunk_text"]]
        for chunk in retrieved_chunks
    ]

    scores = reranker.predict(pairs)

    reranked_chunks = []

    for chunk, score in zip(
        retrieved_chunks,
        scores
    ):
        reranked_chunk = chunk.copy()

        # Preserve the original vector distance
        reranked_chunk["original_distance"] = chunk["distance"]

        # Add the cross-encoder relevance score
        reranked_chunk["rerank_score"] = float(score)

        reranked_chunks.append(
            reranked_chunk
        )

    # Higher cross-encoder score = more relevant
    reranked_chunks.sort(
        key=lambda result: result["rerank_score"],
        reverse=True
    )

    # Keep only the final top-k chunks
    return reranked_chunks[:top_k]