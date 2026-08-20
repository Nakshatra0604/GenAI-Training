# GenAI Document Processing and Semantic Search

## Overview

This project implements a document preprocessing and semantic retrieval
pipeline. It prepares approved documents, sanitizes sensitive values,
cleans and chunks the documents, generates vector embeddings, stores them
in a persistent ChromaDB index, and retrieves relevant document chunks for
user questions.

The project currently covers the Day 5 document preprocessing and Day 6
vector indexing and semantic search activities. Day 7 work will continue
in the same project folder.

---

## Project Structure

GenAI_Day-5/
│
├── cleaned_documents/          # Cleaned document files
├── documents/                  # Sanitized document files
├── raw_documents/              # Original source documents
├── vector_store/               # Persistent ChromaDB vector index
│
├── sanitize_documents.py       # Sanitizes sensitive document values
├── clean_documents.py          # Normalizes and cleans document text
├── chunk_documents.py          # Splits cleaned documents into chunks
├── chunk_quality_review.py     # Performs chunk quality checks
├── chunk_quality_review.md     # Chunk quality review output
├── chunks.jsonl                # Normalized chunk dataset
│
├── generate_embeddings.py      # Generates and reuses embeddings
├── create_vector.py            # Creates the ChromaDB vector index
├── embeddings.jsonl            # Chunk embeddings and metadata
│
├── semantic_search.py          # Reusable semantic search function
├── filter_demo.py              # Metadata-filtered search demonstration
├── retrieval_test_set.json     # 10-question retrieval test set
├── test_retrival.py            # Retrieval test runner
├── retrieval_results.json      # Detailed retrieval test results
│
├── requirements.txt            # Python dependencies
├── .env                        # API and model configuration
└── README.md                   # Project documentation

---

# Day 05 — Prepare Documents, Chunks, and Retrieval Metadata

## Practical Goal

Create a reliable preprocessing pipeline that converts approved documents
into traceable chunks with complete retrieval metadata.

## Implementation

### 1. Collect and Sanitize Documents

sanitize_documents.py - reads Markdown documents from raw_documents/,
redacts configured sensitive values, and writes the sanitized documents to
`documents/` while preserving the original folder structure.

### 2. Load and Clean Text

`clean_documents.py` reads the sanitized Markdown documents, normalizes
line endings and whitespace, removes excessive blank lines, removes empty
Markdown sections, and preserves meaningful headings.

The cleaned documents are stored in `cleaned_documents/`.

### 3. Configurable Chunking

`chunk_documents.py` splits cleaned documents into chunks while preserving
Markdown heading-based sections.

The chunking configuration is:

- Chunk size: `1000`
- Chunk overlap: `150`

The resulting chunks are stored in `chunks.jsonl`.

### 4. Attach Metadata

Each chunk contains metadata including:

- chunk_id
- document_id
- title
- source_path
- updated_at
- chunk_index
- category

### 5. Chunk Quality Review

chunk_quality_review.py inspects representative short, long, and
structured documents and checks for:

- Empty chunks
- Heading/content split issues
- Excessive overlap

The review is written to:

chunk_quality_review.md


The review also records the chunk-indexing issue that was identified and
corrected so that chunk indexes continue sequentially across a document.

## Day 05 Required Deliverables

- Preprocessing scripts for sanitizing, cleaning, and chunking documents
- Normalized chunk dataset in JSONL format
- Metadata attached to every chunk
- Chunk-quality review file with representative examples

## Day 05 Completion Gate

-  Documents are processed through the preprocessing pipeline.
-  Chunks contain source-traceable metadata.
-  Empty chunks are checked during quality review.
-  Chunk size and overlap are configurable in chunk_documents.py.

---

# Day 06 — Build Vector Indexing and Semantic Search

## Practical Goal

Store document embeddings and retrieve the most relevant chunks with
retrieval distance and metadata.

## Implementation

### 1. Generate Embeddings

`generate_embeddings.py` reads `chunks.jsonl` and generates embeddings in
batches of 20 chunks.

The script records the configured embedding model and uses a SHA-256
content hash to identify unchanged chunks and reuse existing embeddings
when possible.

The resulting records are stored in:

```text
embeddings.jsonl
```

### 2. Create the Vector Index

`create_vector.py` loads the generated embeddings and stores them in a
persistent ChromaDB collection named:

```text
document_chunks
```

The persistent index is stored in:

```text
vector_store/
```

### 3. Implement Top-K Search

`semantic_search.py` provides the reusable `search_chunks()` function.

The retrieval flow is:

```text
Question
   ↓
Question Embedding
   ↓
ChromaDB Vector Search
   ↓
Top-K Chunks
   ↓
Chunk Text + Distance + Metadata
```

The function supports:

- Configurable `top_k`
- Optional `category` metadata filtering
- Optional `max_distance` threshold

Returned search information includes:

- `chunk_text`
- `distance`
- `document_id`
- `title`
- `source_path`

### 4. Metadata Filtering

`filter_demo.py` demonstrates metadata-filtered retrieval using:

category="engineering"

The search is therefore restricted to chunks whose metadata category is
`engineering`.

### 5. Retrieval Test Set

`retrieval_test_set.json` contains 10 manually selected questions with
their expected source document IDs.

`test_retrival.py` runs the questions through `search_chunks()` using
`top_k=3` and checks whether the expected document appears in the top three
results.

The detailed results are saved to:

retrieval_results.json


## Day 06 Required Deliverables

- Populated vector index for the Day 5 chunks
- Reusable semantic search function
- 10-question retrieval dataset with expected documents
- Retrieval result report containing retrieved distances and metadata

## Day 06 Completion Gate

-  Semantic search returns the expected document within the top three
   results for the tested questions.
-  Search results contain source metadata required for later retrieval
   and citation workflows.
-  Index creation and retrieval commands are documented below.
- A metadata-filtered search is demonstrated using filter_demo.py.

## Day 06 Retrieval Result

The retrieval test produced:

```text
10/10 expected documents found in the top 3 results
Top-3 hit rate: 100%
```

### Successful Retrieval Examples

**Example 1**

Question:

What should be considered during the planning stage before implementation begins?


Expected document:

DOC-016


The expected document was retrieved in the top three results.

**Example 2**

Question:

What is the process for requesting software that is not available in the standard IT catalog?


Expected document:

DOC-009

The expected document was retrieved as the first result.

### Weak Retrieval Example

Question:

What should an employee do if their account is suspected to be compromised?

Expected document:

DOC-007


The expected document was retrieved in the top three results, but appeared
at rank three. This is a weaker retrieval result that can be improved during
advanced RAG work.

---

# How to Run

Activate the project virtual environment before running the scripts.

### Generate Embeddings

python generate_embeddings.py

### Create the ChromaDB Vector Index

python create_vector.py

### Demonstrate Metadata Filtering

python filter_demo.py

### Run the Retrieval Test Set

python test_retrival.py

The detailed retrieval report is generated as:

retrieval_results.json

---

## Current Status

### Day 05

Document sanitization, cleaning, configurable chunking, metadata
attachment, and chunk-quality review have been implemented.

### Day 06

Embedding generation, persistent ChromaDB indexing, top-K semantic search,
metadata filtering, retrieval testing, and retrieval result reporting have
been implemented.

### Day 07

To be continued in the same project folder.