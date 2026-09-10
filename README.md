# GenAI Document Processing and Semantic Search

## Overview

This project implements a document preprocessing, semantic search, and
baseline RAG retrieval pipeline.

The pipeline prepares approved documents, sanitizes sensitive values,
cleans and chunks the documents, generates vector embeddings, stores them
in a persistent ChromaDB index, retrieves relevant document chunks for
user questions, and prepares the retrieved evidence as context for
generation.

The project currently covers Day 5, Day 6, and Day 7 activities.

---

# Project Structure

```text
GenAI_Day-5/
│
├── raw_documents/                         # Original source documents
├── documents/                             # Sanitized document files
├── cleaned_documents/                     # Cleaned document files
├── vector_store/                          # Persistent ChromaDB vector index
│
├── sanitize_documents.py                  # Sanitizes sensitive document values
├── clean_documents.py                     # Loads and cleans document text
├── chunk_documents.py                     # Splits cleaned documents into chunks
├── chunk_quality_review.py                # Performs chunk quality checks
├── chunk_quality_review.md                # Chunk quality review output
├── chunks.jsonl                           # Normalized chunk dataset
│
├── generate_embeddings.py                 # Generates and reuses embeddings
├── create_vector_index.py                 # Creates the ChromaDB vector index
├── embeddings.jsonl                       # Chunk embeddings and metadata
│
├── semantic_search.py                     # Reusable semantic search function
├── filter_demo.py                         # Metadata-filtered search demonstration
├── retrieval_test_set.json                # Retrieval test questions
├── test_retrieval.py                      # Day 6 retrieval test runner
├── retrieval_results.json                 # Retrieval test results
│
├── ingest.py                              # Complete document ingestion pipeline
├── retrieve.py                            # Retrieval pipeline
├── generate.py                            # Grounded answer generation pipeline
├── grounded_prompt.py                     # Grounded answer prompt
├── answer_model.py                        # Validated answer response model
├── citation_validator.py                  # Validates answer citations
├── test_pipeline.py                       # Day 7 integration tests
│
├── baseline_config.yaml                   # Frozen Day 9 baseline configuration
├── day9_weak_questions.json                # Five weak retrieval cases
├── day9_failure_analysis.json             # Day 9 retrieval failure analysis
├── day9_experiment_matrix.json            # Controlled Day 9 experiment plan
├── day9_baseline_metrics.py               # Day 9 baseline metric runner
├── day9_baseline_metrics.json             # Day 9 baseline metric results
│
├── day10_experiments.py                   # Executes planned Day 10 experiments
├── day10_experiment_results.json          # Day 10 experiment results
├── query_rewriter.py                      # Reusable query rewriting component
├── day10_query_rewrite_experiment.py      # Query rewriting experiment
├── day10_query_rewrite_results.json       # Query rewriting results
├── reranker.py                            # Cross-encoder reranking component
├── day10_reranking_experiment.py          # Cross-encoder reranking experiment
├── day10_reranking_results.json           # Reranking results
├── day10_regression_test.py               # Full retrieval regression test
├── day10_regression_results.json          # Regression test results
├── day10_before_after_retrieval_report.md # Day 10 before-and-after report
├── day10_final_config.yaml                # Selected Day 10 configuration
│
├── requirements.txt                       # Python dependencies
├── .env                                   # API and model configuration
├── .env.example                           # Example environment configuration
└── README.md                              # Project documentation
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

### Day 07 — Implement Baseline RAG Ingestion and Retrieval

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

The retrieved evidence contains the document ID, title, source path,
retrieval distance, and chunk text.

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

The resulting output contains only the selected retrieved evidence in a
consistent, traceable format.

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

They verify ingest-then-retrieve behavior and failed-document handling.

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

The vector index contains 172 records after repeated ingestion, without
uncontrolled growth from duplicate unchanged chunks.

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

**Day 07 implementation and pipeline-level verification completed successfully.**

# Day 08 — Add Grounded Generation, Citations, and Abstention

## Practical Goal

Generate answers only from retrieved evidence and return valid citations or a useful abstention response.

Day 8 extends the Day 7 retrieval pipeline into a grounded question-answering pipeline. The generation layer now uses only the retrieved evidence, validates citations against the supplied source chunks, and abstains when sufficient evidence is not available.

---

## Implementation

### 1. Grounded Answer Prompt

A grounded answer prompt was implemented in `grounded_prompt.py`.

The prompt instructs the generation model to:

- Use only the provided context.
- Avoid outside knowledge and unsupported assumptions.
- Answer only the portion of a question supported by the retrieved evidence.
- Clearly identify information that is not available in the provided context.
- Cite factual claims using the document IDs supplied with the retrieved chunks.
- Never invent document IDs or citations.
- Abstain when the available evidence is insufficient.

The expected citation format is:

```text
[DOC-009]
```

This ensures that generated answers remain traceable to the retrieved evidence.

---

### 2. Validated Answer Response Model

A structured Pydantic response model was implemented in `answer_model.py`.

The response contains:

| Field | Description |
|---|---|
| `answer` | Grounded answer generated from the retrieved evidence |
| `sources` | Source documents referenced by the answer |
| `chunks` | Evidence chunks used for generation |
| `scores` | Retrieval distance scores for the selected chunks |
| `status` | Indicates `answered` or `insufficient_evidence` |

This ensures that the final response follows a consistent and validated structure.

Partially answerable questions are handled using the `answered` status while explicitly identifying the unsupported portion of the question in the answer. A separate `partially_answered` status is not required by the Day 8 specification.

---

### 3. Citation Validation

Citation validation was implemented in `citation_validator.py`.

The validator compares citations generated by the model against the source labels supplied in the generation context.

The validation process ensures that:

- At least one citation is present for an answered response.
- Every cited document ID exists in the supplied context.
- Invalid or fabricated document references are rejected.
- Valid citations are mapped back to their complete source references.

This prevents the generation model from citing documents that were not actually retrieved and provided as evidence.

---

### 4. Evidence Threshold

An evidence threshold was introduced before generation.

The current retrieval distance threshold is:

```text
max_distance = 0.8
```

Only retrieved chunks that satisfy the configured threshold are considered suitable evidence for generation.

The generation pipeline therefore follows:

```text
Retrieved Results
        ↓
Evidence Threshold
        ↓
Selected Evidence
        ↓
Grounded Context
        ↓
LLM Generation
```

Duplicate chunks are removed before the final context is supplied to the model.

---

### 5. Abstention

An abstention mechanism was added to `generate.py`.

If no retrieved evidence passes the configured threshold, the system does not generate an unsupported answer.

Instead, it returns:

```text
Insufficient evidence to answer the question from the provided documents.
```

with the response status:

```text
insufficient_evidence
```

The sources, chunks, and scores are returned as empty lists for an abstained response.

This provides a safe fallback for questions that cannot be answered from the available documents.

---

### 6. Grounded Generation Pipeline

The Day 8 generation pipeline combines retrieval, evidence selection, grounded generation, citation validation, and response validation.

The resulting flow is:

```text
User Question
      ↓
Retrieve Evidence
      ↓
Apply Evidence Threshold
      ↓
Select Relevant Chunks
      ↓
Build Grounded Context
      ↓
Generate Answer
      ↓
Validate Citations
      ↓
Validate Response
      ↓
Return Grounded Answer
      │
      └── Insufficient/Invalid Evidence
                    ↓
                Abstention
```

The existing retrieval components are reused rather than creating a separate retrieval implementation.

---

# Day 8 Testing

Three scenarios were tested to verify grounded generation and abstention behavior.

## Test 1 — Answerable Question

### Question

> What is the process for requesting software that is not available in the standard IT catalog?

### Result

The system successfully retrieved the relevant software installation request document and generated an answer based on the retrieved evidence.

The response included a valid citation:

```text
[DOC-009]
```

The citation was successfully mapped to:

```text
DOC-009:it\DOC-009_software_installation_request_process.md
```

The final response status was:

```text
answered
```

### Outcome

**PASS**

The answer was grounded in the retrieved evidence and contained a valid source reference.

---

## Test 2 — Partially Answerable Question

### Question

> What is the process for requesting software that is not in the IT catalog, and who is responsible for approving the request?

### Result

The retrieved evidence supported the software request process, including:

- Submitting the request through the IT ticketing system.
- Providing the software name.
- Providing business justification.
- Providing relevant data-handling information.
- Review of the request within the specified processing period.
- Additional security review for requests involving sensitive data.
- Installation or further instructions after approval.

However, the retrieved evidence did not explicitly identify who is responsible for approving the request.

The system therefore answered the supported portion and explicitly stated that the approval responsibility was not specified in the provided context.

### Outcome

**PASS**

The system avoided making an unsupported assumption about the approval owner.

---

## Test 3 — Unanswerable Question

### Question

> What is the company's policy for international business travel?

### Result

The available evidence did not provide sufficient information to answer the question.

The system correctly returned:

```text
Insufficient evidence to answer the question from the provided documents.
```

with:

```text
status = insufficient_evidence
```

No unsupported answer or fabricated citation was generated.

### Outcome

**PASS**

The system safely abstained when sufficient evidence was unavailable.

---

# Required Deliverables

| Deliverable | Status |
|---|---|
| Grounded answer prompt | Completed |
| Validated answer response schema | Completed |
| Citation mapping and validation | Completed |
| Evidence threshold and filtering | Completed |
| Abstention behavior | Completed |
| Answerable test case | Completed |
| Partially answerable test case | Completed |
| Unanswerable test case | Completed |
| Example cited answer | Completed |
| Example abstention response | Completed |

---

# Completion Gate

| Requirement | Result |
|---|---|
| Every answered response has at least one valid source | PASS |
| No citation refers to evidence outside the supplied context | PASS |
| Unsupported questions produce a clear abstention | PASS |
| Partially supported questions do not trigger unsupported assumptions | PASS |
| Evidence threshold is applied before generation | PASS |
| Final responses follow the validated response schema | PASS |
| Pipeline is reproducible with one command | PASS |

---

# End-of-Day Evidence

### Cited Answer

An answerable software-request question successfully produced a grounded answer with a valid `[DOC-009]` citation mapped to the retrieved source document.

### Unsupported Question

An unsupported international business travel question was safely declined with:

```text
Insufficient evidence to answer the question from the provided documents.
```

This confirms that the system can distinguish between supported evidence and insufficient evidence instead of guessing.

---

# Day 8 Final Outcome

Day 8 successfully extends the retrieval pipeline into a grounded RAG question-answering system.

The system now:

- Generates answers from retrieved evidence only.
- Applies an evidence threshold before generation.
- Provides traceable source citations.
- Validates citations against the supplied evidence.
- Returns structured Pydantic responses.
- Handles partially supported questions without unsupported assumptions.
- Abstains when the available evidence is insufficient.

The final Day 8 pipeline is therefore:

**Retrieve → Filter Evidence → Generate Grounded Answer → Validate Citations → Validate Response → Answer or Abstain**

The pipeline can be reproduced using:

```bash
python generate.py
```

---

# Day 09 — Diagnose Retrieval Failures and Define Controlled Experiments

## Practical Goal

Use the weakest baseline retrieval questions to identify retrieval problems and design measurable, controlled experiments where only one primary retrieval variable is changed at a time.

Day 9 focuses on understanding why some retrieval cases are weaker than others, freezing the existing retrieval configuration as a baseline, classifying observed retrieval issues, and defining experiments that can be evaluated objectively.

---

## Implementation

### 1. Freeze the Baseline Configuration

The current retrieval configuration was frozen before making retrieval improvements so that all Day 10 experiments could be compared against a stable baseline.

The frozen configuration is stored in:

```text
baseline_config.yaml

