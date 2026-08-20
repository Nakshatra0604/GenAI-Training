import json
import os
import hashlib
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

INPUT_FILE = Path("chunks.jsonl")
OUTPUT_FILE = Path("embeddings.jsonl")

BATCH_SIZE = 20 


client = OpenAI(
    api_key = API_KEY,
    base_url = "https://openrouter.ai/api/v1"
)
 
# reads chunks.jsonl and convert every json line into python dictionary

def load_chunks():
    chunks = []

    with INPUT_FILE.open("r",encoding = "utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))
    return chunks


# batching function

def create_batches(items, batch_size):
    batches = []

    for start in range(0, len(items), batch_size):
        batches.append(items[start:start + batch_size])

    return batches

def generate_embeddings(texts):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        encoding_format="float"
    )

    return response.data



# giving hash to the contents

def get_content_hash(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

def load_existing_embeddings():
    existing = {}

    if not OUTPUT_FILE.exists():
        return existing

    with OUTPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                record = json.loads(line)
                existing[record["chunk_id"]] = record

    return existing

def find_chunks_needing_embeddings(chunks, existing_embeddings):
    chunks_to_embed = []
    reused_embeddings = []

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        content_hash = get_content_hash(chunk["text"])

        existing = existing_embeddings.get(chunk_id)

        if existing and existing.get("content_hash") == content_hash:
            reused_embeddings.append(existing)
        else:
            chunk["content_hash"] = content_hash
            chunks_to_embed.append(chunk)

    return chunks_to_embed, reused_embeddings

def process_embeddings(chunks_to_embed):
    new_embeddings = []

    batches = create_batches(chunks_to_embed, BATCH_SIZE)

    for batch_number, batch in enumerate(batches, start=1):

        texts = [chunk["text"] for chunk in batch]

        print(
            f"Processing batch {batch_number}/{len(batches)} "
            f"({len(batch)} chunks)..."
        )

        embeddings = generate_embeddings(texts)

        for chunk, embedding in zip(batch, embeddings):

            record = {
                **chunk,
                "embedding": embedding.embedding,
                "embedding_model": EMBEDDING_MODEL,
            }

            new_embeddings.append(record)

    return new_embeddings

chunks = load_chunks()

print(f"Loaded {len(chunks)} chunks.")

existing_embeddings = load_existing_embeddings()

chunks_to_embed, reused_embeddings = find_chunks_needing_embeddings(
    chunks,
    existing_embeddings
)

print(f"Chunks needing embeddings: {len(chunks_to_embed)}")
print(f"Existing embeddings reused: {len(reused_embeddings)}")

new_embeddings = process_embeddings(chunks_to_embed)

all_embeddings = reused_embeddings + new_embeddings

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    for record in all_embeddings:
        file.write(
            json.dumps(record, ensure_ascii=False) + "\n"
        )

print(f"Saved {len(all_embeddings)} embeddings to {OUTPUT_FILE}")