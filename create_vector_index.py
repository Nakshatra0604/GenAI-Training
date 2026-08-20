import chromadb
import json

from pathlib import Path

client = chromadb.PersistentClient(path="vector_store")

collection = client.get_or_create_collection(
    name = "document_chunks"
)

INPUT_FILE = Path("embeddings.jsonl")

def load_embeddings():
    records  =[]

    with INPUT_FILE.open("r", encoding = "utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records

records = load_embeddings()

print(f"Loaded {len(records)} embedding records")

ids = [record["chunk_id"] for record in records]

embeddings = [record["embedding"] for record in records]

documents = [record["text"] for record in records]

metadatas = [
    {
        "document_id": record["document_id"],
        "title": record["title"],
        "source_path": record["source_path"],
        "category": record["category"],
        "chunk_index": record["chunk_index"],
        "content_hash": record["content_hash"],
        "embedding_model": record["embedding_model"],
    }
    for record in records
]

collection.add(
    ids=ids,
    embeddings=embeddings,
    documents=documents,
    metadatas=metadatas
)

print(f"Total records in ChromaDB: {collection.count()}")