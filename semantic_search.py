import os
import chromadb

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

client = OpenAI(
    api_key = API_KEY,
    base_url = "https://openrouter.ai/api/v1"
)

chroma_client = chromadb.PersistentClient(
    path = "vector_store"
)

collection = chroma_client.get_collection(
    name = "document_chunks"
    )

# query embedding function 

def create_query_embedding(question):
    response = client.embeddings.create(
        model = EMBEDDING_MODEL,
        input = [question],
        encoding_format = "float"
    )

    return response.data[0].embedding

def search_chunks(
    question,
    top_k=3,
    category=None,
    max_distance=None
):
    query_embedding = create_query_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"category": category} if category else None
    )

    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    search_results = []

    for document, distance, metadata in zip(
        documents,
        distances,
        metadatas
    ):
        if max_distance is not None and distance > max_distance:
            continue

        result = {
            "chunk_text": document,
            "distance": distance,
            "document_id": metadata["document_id"],
            "title": metadata["title"],
            "source_path": metadata["source_path"],
        }

        search_results.append(result)

    return search_results