from clean_documents import process_documents as clean_documents
from chunk_documents import process_documents as chunk_documents
from generate_embeddings import process_embeddings_pipeline
from create_vector_index import create_vector_index


def ingest_documents():

    print("Starting ingestion pipeline...")

    # Step 1: Load and clean documents
    print("\nStep 1: Cleaning documents...")
    clean_documents()

    # Step 2: Chunk cleaned documents
    print("\nStep 2: Creating chunks...")
    chunk_documents()

    # Step 3: Generate embeddings
    print("\nStep 3: Generating embeddings...")
    process_embeddings_pipeline()

    # Step 4: Store embeddings in vector database
    print("\nStep 4: Creating vector index...")
    create_vector_index()

    print("\nIngestion pipeline completed.")


if __name__ == "__main__":
    ingest_documents()