# GenAI Document Processing and Semantic Search

## Overview

This project implements a document preprocessing, semantic search, and
baseline RAG retrieval pipeline.

The pipeline prepares approved documents, sanitizes sensitive values,
cleans and chunks the documents, generates vector embeddings, stores them
in a persistent ChromaDB index, retrieves relevant document chunks for
user questions, and prepares retrieved evidence as context for generation.

The project currently covers Day 5, Day 6, and Day 7 activities.

---

## Project Structure

GenAI-Training/
│
├── cleaned_documents/          # Cleaned document files
├── documents/                  # Sanitized document files
├── raw_documents/             # Original source documents
├── vector_store/              # Persistent ChromaDB vector index
│
├── sanitize_documents.py      # Sanitizes sensitive document values
├── clean_documents.py        # Loads and cleans document text
├── chunk_documents.py        # Splits cleaned documents into chunks
├── chunk_quality_review.py   # Performs chunk quality checks
├── chunk_quality_review.md   # Chunk quality review output
├── chunks.jsonl              # Normalized chunk dataset
│
├── generate_embeddings.py    # Generates and reuses embeddings
├── create_vector_index.py    # Creates the ChromaDB vector index
├── embeddings.jsonl          # Chunk embeddings and metadata
│
├── semantic_search.py        # Reusable semantic search function
├── filter_demo.py            # Metadata-filtered search demonstration
├── retrieval_test_set.json   # 10-question retrieval test set
├── test_retrieval.py         # Retrieval test runner
├── retrieval_results.json    # Detailed retrieval test results
│
├── ingest.py                 # Complete document ingestion pipeline
├── retrieve.py               # Retrieval pipeline
├── generate.py               # Retrieval context preparation
├── test_pipeline.py          # Day 7 integration tests
│
├── requirements.txt          # Python dependencies
├── .env                      # API and model configuration
└── README.md                 # Project documentation

---

# Day 05 — Prepare Documents, Chunks, and Retrieval Metadata

## Practical Goal

Create a reliable preprocessing pipeline that converts approved documents
into traceable chunks with complete retrieval metadata.

## Implementation

### 1. Collect and Sanitize Documents

`sanitize_documents.py` reads Markdown documents from `raw_documents/`,
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

- `chunk_id`
- `document_id`
- `title`
- `source_path`
- `updated_at`
- `chunk_index`
- `category`

### 5. Chunk Quality Review

`chunk_quality_review.py` inspects representative short, long, and
structured documents and checks for:

- Empty chunks
- Heading/content split issues
- Excessive overlap

The review is written to:

`chunk_quality_review.md`

The review also records the chunk-indexing issue that was identified and
corrected so that chunk indexes continue sequentially across a document.

## Day 05 Required Deliverables

- Preprocessing scripts for sanitizing, cleaning, and chunking documents
- Normalized chunk dataset in JSONL format
- Metadata attached to every chunk
- Chunk-quality review file with representative examples

## Day 05 Completion Gate

- Documents are processed through the preprocessing pipeline.
- Chunks contain source-traceable metadata.
- Empty chunks are checked during quality review.
- Chunk size and overlap are configurable in `chunk_documents.py`.

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

`embeddings.jsonl`

### 2. Create the Vector Index

`create_vector_index.py` loads the generated embeddings and stores them in a
persistent ChromaDB collection named:

`document_chunks`

The persistent index is stored in:

`vector_store/`

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

`category="engineering"`

The search is therefore restricted to chunks whose metadata category is
`engineering`.

### 5. Retrieval Test Set

`retrieval_test_set.json` contains 10 manually selected questions with
their expected source document IDs.

`test_retrieval.py` runs the questions through `search_chunks()` using
`top_k=3` and checks whether the expected document appears in the top three
results.

The detailed results are saved to:

`retrieval_results.json`

## Day 06 Required Deliverables

- Populated vector index for the Day 5 chunks
- Reusable semantic search function
- 10-question retrieval dataset with expected documents
- Retrieval result report containing retrieved distances and metadata

## Day 06 Completion Gate

- Semantic search returns the expected document within the top three
  results for the tested questions.
- Search results contain source metadata required for later retrieval
  and citation workflows.
- Index creation and retrieval commands are documented below.
- A metadata-filtered search is demonstrated using `filter_demo.py`.

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

`DOC-016`

The expected document was retrieved in the top three results.

**Example 2**

Question:

What is the process for requesting software that is not available in the standard IT catalog?

Expected document:

`DOC-009`

The expected document was retrieved as the first result.

### Weak Retrieval Example

Question:

What should an employee do if their account is suspected to be compromised?

Expected document:

`DOC-007`

The expected document was retrieved in the top three results, but appeared
at rank three. This is a weaker retrieval result that can be improved during
advanced RAG work.

---

# Day 07 — Implement Baseline RAG Ingestion and Retrieval

## Practical Goal

Connect document loading, cleaning, chunking, embedding generation, vector
indexing, semantic retrieval, and context preparation into one simple and
understandable RAG pipeline.

## Implementation

### 1. Separate RAG Modules

Day 7 introduces separate modules for the main RAG stages:

- `ingest.py` — connects the document ingestion stages into one pipeline
- `retrieve.py` — provides the retrieval entry point
- `generate.py` — prepares retrieved evidence as context for generation
- `test_pipeline.py` — performs pipeline-level integration checks

Each stage remains independently callable so that individual stages can be
tested and failures can be diagnosed without using a large orchestration
framework.

### 2. Build the Ingestion Flow

`ingest.py` provides the `ingest_documents()` function and connects the
existing document-processing modules into one ingestion pipeline.

The ingestion flow is:

```text
Sanitized Documents
        ↓
Load and Clean
        ↓
Create Chunks
        ↓
Generate Embeddings
        ↓
Create Vector Index
```

The complete ingestion pipeline can be executed using:

```bash
python ingest.py
```

During verification, the pipeline successfully processed 30 Markdown
documents, created 172 chunks, reused the existing embeddings for unchanged
chunks, and maintained 172 records in the ChromaDB vector index.

Re-ingestion behavior is handled using the SHA-256 content hash implemented
in `generate_embeddings.py`. When a chunk has not changed, its existing
embedding can be reused instead of generating a new embedding.

### 3. Build the Retrieval Flow

`retrieve.py` provides the `retrieve()` function and uses the reusable
`search_chunks()` function from `semantic_search.py`.

The retrieval flow is:

```text
User Question
      ↓
Query Embedding
      ↓
ChromaDB Vector Search
      ↓
Top-K Results
      ↓
Retrieved Chunks + Distance + Metadata
```

The default retrieval configuration is:

- `top_k = 3`
- `category = None`
- `max_distance = None`

The retrieval command is:

```bash
python retrieve.py
```

The command accepts a question and displays the retrieved evidence along
with:

- Document ID
- Title
- Source path
- Retrieval distance
- Chunk text

For example, the known question:

```text
What is the process for requesting software that is not available
in the standard IT catalog?
```

retrieved `DOC-009` as the first result within the configured Top-K results.

The retrieval stage continues to use the reusable semantic search
implementation from Day 6 rather than duplicating the vector-search logic.

### 4. Prepare Context for Generation

`generate.py` provides the `prepare_context()` function.

This stage does not generate the final natural-language answer. It prepares
the evidence returned by the retrieval stage so that it can be passed to a
future generation step.

The context preparation performs three operations:

- Removes duplicate retrieved chunks
- Adds stable source labels
- Limits the final context to the selected evidence

The context preparation flow is:

```text
Retrieved Evidence
       ↓
Remove Duplicate Chunks
       ↓
Add Stable Source Labels
       ↓
Limit Selected Evidence
       ↓
Final Context
```

Each retrieved chunk is given a stable source label containing the document
ID and source path.

Example:

```text
[Source: DOC-009:it\DOC-009_software_installation_request_process.md]
```

The context preparation command is:

```bash
python generate.py
```

The resulting output contains the selected retrieved evidence in a
consistent and traceable format.

Day 7 prepares the context for generation; it does not yet generate the
final natural-language answer.

### 5. Pipeline-Level Checks

`test_pipeline.py` contains integration checks for the Day 7 pipeline.

The main integration test verifies the following flow:

```text
Ingestion
    ↓
Retrieval
    ↓
Context Preparation
```

The test uses a known question and verifies that:

- Documents can be ingested successfully.
- Retrieval returns relevant evidence.
- The expected document (`DOC-009`) is retrieved.
- Final context is successfully prepared.
- Stable source labels are present in the final context.

A second test verifies failed-document handling. A document-processing
failure is simulated and recorded, while processing continues for the
remaining documents.

The pipeline checks can be executed using:

```bash
python test_pipeline.py
```

The completed verification produced:

```text
Ingest → Retrieve → Context integration test passed.
Failed-document handling test passed.
All Day 7 pipeline checks passed.
```

---

## Day 07 Required Deliverables

### Separate Ingestion and Retrieval Modules

Implemented using:

- `ingest.py`
- `retrieve.py`

Context preparation is separated into:

- `generate.py`

### One Command for Ingestion

The complete ingestion pipeline can be executed using:

```bash
python ingest.py
```

### One Command for Retrieval Context

A question can be entered through:

```bash
python generate.py
```

The command retrieves the relevant evidence and prepares the final
source-labelled context.

### Integration Tests

Pipeline-level integration tests are implemented in:

```text
test_pipeline.py
```

They verify ingest-then-retrieve behavior, context preparation, and
failed-document handling.

---

## Day 07 Completion Gate

### Basic Flow Visible in Code

The complete basic flow is implemented using small, independently callable
Python modules rather than a large orchestration framework.

```text
Ingestion
   ↓
Retrieval
   ↓
Context Preparation
```

### Controlled Re-ingestion

Re-ingestion uses the existing SHA-256 content hash to identify unchanged
chunks and reuse their embeddings.

Repeated ingestion maintains the expected 172 embedding records instead of
creating uncontrolled duplicate embedding records for unchanged chunks.

### Stable Source Labels

Retrieved context includes stable source labels based on the document ID
and source path.

Example:

```text
[Source: DOC-009:it\DOC-009_software_installation_request_process.md]
```

This keeps the prepared context traceable to its source document.

### Integration Tests

The Day 7 pipeline-level checks completed successfully:

```text
Ingest → Retrieve → Context integration test passed.
Failed-document handling test passed.
All Day 7 pipeline checks passed.
```

---

## Day 07 End-of-Day Evidence

A complete document-to-retrieval flow was verified using the IT software
installation request document (`DOC-009`).

The document was processed through the existing preprocessing and ingestion
pipeline:

```text
Raw Document
      ↓
Sanitization
      ↓
Cleaning
      ↓
Chunking
      ↓
Embedding Generation
      ↓
ChromaDB Vector Index
```

A known question was then submitted to the retrieval pipeline:

```text
What is the process for requesting software that is not available
in the standard IT catalog?
```

The retrieval stage returned `DOC-009` as the first result among the Top-3
results.

The retrieved evidence was then passed to `generate.py`, where it was
prepared as generation-ready context using a stable source label:

```text
[Source: DOC-009:it\DOC-009_software_installation_request_process.md]
```

The Day 7 integration tests confirmed successful ingestion, retrieval,
context preparation, stable source labelling, and failed-document handling.

---

## Day 07 Verification Summary

| Area | Status |
|---|---|
| Separate ingestion module | Completed |
| Separate retrieval module | Completed |
| Context preparation module | Completed |
| Complete ingestion command | Verified |
| Top-K retrieval | Verified |
| Stable source labels | Verified |
| Duplicate context removal | Verified |
| Context limiting | Verified |
| Re-ingestion handling | Verified |
| Ingest → Retrieve integration | Passed |
| Failed-document handling | Passed |

**Day 07 implementation and pipeline-level verification completed successfully.**

---

# How to Run

Activate the project virtual environment before running the scripts.

### Generate Embeddings

```bash
python generate_embeddings.py
```

### Create the ChromaDB Vector Index

```bash
python create_vector_index.py
```

### Demonstrate Metadata Filtering

```bash
python filter_demo.py
```

### Run the Day 6 Retrieval Test Set

```bash
python test_retrieval.py
```

The detailed retrieval report is generated as:

`retrieval_results.json`

### Run the Day 7 Ingestion Pipeline

```bash
python ingest.py
```

### Run the Day 7 Retrieval Flow

```bash
python retrieve.py
```

### Prepare Retrieval Context

```bash
python generate.py
```

### Run Day 7 Pipeline Integration Tests

```bash
python test_pipeline.py
```

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

Baseline RAG ingestion, retrieval, context preparation, re-ingestion
handling, and pipeline-level integration tests have been implemented and
verified successfully.