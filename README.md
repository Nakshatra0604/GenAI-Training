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
├── retrieve.py                            # Day 10 retrieval pipeline with reranking
├── generate.py                            # Grounded answer generation pipeline
├── grounded_prompt.py                     # Grounded answer prompt and prompt version
├── answer_model.py                        # Validated answer response model
├── citation_validator.py                  # Validates answer citations
├── test_pipeline.py                       # Day 7 integration tests
│
├── baseline_config.yaml                   # Frozen Day 9 baseline configuration
├── day9_weak_questions.json               # Five weak retrieval cases
├── day9_failure_analysis.json             # Day 9 retrieval failure analysis
├── day9_experiment_matrix.json            # Controlled Day 9 experiment plan
├── day9_baseline_metrics.py              # Day 9 baseline metric runner
├── day9_baseline_metrics.json             # Day 9 baseline metric results
│
├── query_rewriter.py                      # Reusable query rewriting component
├── day10_experiments.py                   # Executes planned Day 10 experiments
├── day10_experiment_results.json          # Day 10 experiment results
├── day10_query_rewrite_experiment.py      # Query rewriting experiment
├── day10_query_rewrite_results.json       # Query rewriting results
├── reranker.py                            # Cross-encoder reranking component
├── day10_reranking_experiment.py          # Cross-encoder reranking experiment
├── day10_reranking_results.json           # Day 10 reranking results
├── day10_regression_test.py               # Full retrieval regression test
├── day10_regression_results.json          # Regression test results
├── day10_before_after_retrieval_report.md # Day 10 before-and-after report
├── day10_final_config.yaml                # Selected Day 10 configuration
│
├── api/                                   # FastAPI service layer
│   ├── main.py                            # FastAPI application entry point
│   ├── routes.py                          # API endpoint definitions and observability flow
│   ├── models.py                          # Pydantic request, response, and error models
│   ├── dependencies.py                    # Configuration and dependency readiness checks
│   └── errors.py                          # Custom API/provider error definitions
│
├── observability/                         # SQL request observability layer
│   ├── __init__.py                        # Observability package initialization
│   ├── database.py                        # SQLAlchemy database configuration and sessions
│   ├── observability_models.py            # Request and retrieved-source database models
│   ├── logging_service.py                 # Request and source logging operations
│   └── init_db.py                         # Creates observability database tables
│
├── tests/                                 # API test suite
│   └── test_api.py                        # FastAPI API and error-handling tests
│
├── evaluation/                            # Day 13–14 evaluation framework
│   ├── golden_set.jsonl                   # 25-case golden evaluation dataset
│   ├── dataset_review.md                  # Manual golden dataset review notes
│   ├── run_evals.py                       # End-to-end evaluation runner
│   ├── retrieval_grader.py                # Retrieval quality grader
│   ├── answer_grader.py                   # Answer quality and citation grader
│   ├── review_report.py                   # Per-case review and failure report
│   ├── scorecard.py                       # Evaluation scorecard generator
│   ├── regression_check.py                # One-command regression threshold check
│   └── results/                           # Machine-readable evaluation results
│       ├── evaluation_run_*.json          # Timestamped evaluation run results
│       ├── review_report.json              # Per-case evaluation report
│       └── scorecard.json                  # Baseline evaluation scorecard
│
├── pytest.ini                             # Pytest configuration
├── observability.db                       # Local SQLite observability database
│
├── requirements.txt                       # Python dependencies
├── .env                                   # API and model configuration
├── .env.example                           # Example environment configuration
├── .gitignore                              # Git ignore rules for secrets, environments, and cache
└── README.md                              # Project documentation

----

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

Day 9 focuses on freezing the existing retrieval configuration, analyzing weak retrieval cases, defining controlled experiments, and measuring baseline retrieval performance using reproducible metrics.

---

## Implementation

### 1. Freeze the Baseline Configuration

The existing retrieval configuration was frozen before making retrieval improvements so that later experiments could be compared against a stable baseline.

The frozen configuration is stored in:

​```text
baseline_config.yaml
​```

The baseline configuration records:

- Embedding model: `nvidia/NemoTron-3-Embed-1B:free`
- Chunk size: `1000`
- Chunk overlap: `150`
- Retrieval Top-K: `3`
- Category filter: `None`
- Retrieval distance threshold: `None`
- Generation evidence distance threshold: `0.8`
- Maximum context chunks: `3`
- Prompt version: `current_day8`

The frozen baseline retrieval flow is:

​```text
Question
   ↓
Query Embedding
   ↓
Vector Search
   ↓
Top-3 Results
   ↓
Retrieved Evidence
​```

### 2. Select Five Weak Retrieval Questions

Five weak or potentially problematic retrieval cases were selected from the existing Day 6 and Day 8 retrieval results.

The selected cases are stored in:

​```text
day9_weak_questions.json
​```

The five cases are:

| Case ID | Expected Document | Observed Issue |
|---|---|---|
| DQ-001 | DOC-007 | Expected document ranked third |
| DQ-002 | DOC-016 | Candidate has relatively high retrieval distance |
| DQ-003 | DOC-017 | Less-specific error-related documents also retrieved |
| DQ-004 | DOC-009 | Retrieved evidence does not explicitly identify the approval owner |
| DQ-005 | DOC-014 | Less-specific access-related document also retrieved |

The expected source document for each case is explicitly recorded so that retrieval performance can be measured consistently.

### 3. Analyze Retrieval Failures

The selected cases were analyzed based on their actual retrieved evidence rather than only on assumptions about the retrieval system.

The analysis is stored in:

​```text
day9_failure_analysis.json
​```

The analysis records:

- Failure category
- Likely cause
- Reason based on the retrieved evidence

Examples include:

- `wrong_ranking`
- `low_confidence_candidate`
- `incomplete_context`
- `potential_noisy_context`

The analysis helps identify whether a retrieval problem may be related to vocabulary mismatch, broad queries, semantic overlap, or insufficient retrieved context.

### 4. Define Controlled Experiments

A controlled experiment matrix was created so that each experiment changes only one primary retrieval variable at a time.

The experiment plan is stored in:

​```text
day9_experiment_matrix.json
​```

The planned experiments include:

| Experiment | Case | Primary Variable | Baseline | Experiment |
|---|---|---|---|---|
| EXP-001 | DQ-001 | Query rewrite | Original query | More specific compromised-account query |
| EXP-002 | DQ-002 | Top-K | 3 | 5 |
| EXP-003 | DQ-005 | Top-K | 3 | 2 |
| EXP-004 | DQ-004 | Top-K | 3 | 5 |
| EXP-005 | DQ-003 | Query rewrite | Original query | More specific developer-focused query |

Each experiment includes a reason for the change and an expected outcome.

The experiments are designed so that the effect of the selected variable can be measured without changing multiple retrieval settings simultaneously.

### 5. Measure Baseline Retrieval Metrics

A repeatable baseline metric runner was implemented in:

​```text
day9_baseline_metrics.py
​```

The script loads the five Day 9 weak questions and runs each question through the existing `search_chunks()` retrieval function using the frozen baseline `top_k = 3`.

For every question, the script records:

- Retrieved document IDs
- Retrieval rank
- Retrieval distance
- Expected document rank
- Hit@3
- Recall@3
- Reciprocal Rank

The detailed results are saved to:

​```text
day9_baseline_metrics.json
​```

The baseline metrics include:

- Hit Rate@3
- Recall@3
- Mean Reciprocal Rank (MRR)

---

## Day 09 Baseline Results

The baseline metric runner was executed using:

​```bash
python day9_baseline_metrics.py
​```

The five weak retrieval cases produced the following results:

| Case | Expected Document | Expected Rank | Hit@3 | Reciprocal Rank |
|---|---|---|---|---|
| DQ-001 | DOC-007 | 3 | True | 0.333 |
| DQ-002 | DOC-016 | 1 | True | 1.000 |
| DQ-003 | DOC-017 | 1 | True | 1.000 |
| DQ-004 | DOC-009 | 2 | True | 0.500 |
| DQ-005 | DOC-014 | 1 | True | 1.000 |

Overall baseline metrics:

| Metric | Value |
|---|---|
| Hit Rate@3 | 1.000 |
| Recall@3 | 1.000 |
| MRR | 0.767 |

The results show that all five expected documents were retrieved within the top three results, while the MRR value shows that some expected documents were ranked below the first position.

---

## Day 09 Required Deliverables

| Deliverable | Status |
|---|---|
| Frozen baseline configuration | Completed |
| Five-question failure analysis | Completed |
| Controlled experiment plan | Completed |
| Baseline metric report | Completed |
| Per-question retrieval results | Completed |
| Rerunnable baseline measurement script | Completed |

## Day 09 Completion Gate

| Requirement | Result |
|---|---|
| Every proposed experiment changes only one primary variable | PASS |
| Each weak question has a stated expected source document | PASS |
| Baseline measurements are rerunnable from one command | PASS |
| Failure labels are based on retrieved evidence | PASS |

## Day 09 End-of-Day Evidence

The Day 9 baseline was reproduced using:

​```bash
python day9_baseline_metrics.py
​```

The command successfully loaded all five Day 9 test cases and produced per-question retrieval results.

The final baseline measurements were:

| Metric | Value |
|---|---|
| Hit Rate@3 | 1.000 |
| Recall@3 | 1.000 |
| MRR | 0.767 |

The detailed per-question results were saved to:

​```text
day9_baseline_metrics.json
​```

The five weak cases were analyzed and documented in:

​```text
day9_failure_analysis.json
​```

The controlled retrieval experiments were defined in:

​```text
day9_experiment_matrix.json
​```

The baseline configuration used for the measurements was frozen in:

​```text
baseline_config.yaml
​```

## Day 09 Final Outcome

Day 9 successfully established a reproducible baseline for retrieval analysis.

The project now has:

- A frozen retrieval configuration.
- Five explicitly defined weak retrieval questions.
- Evidence-based failure analysis.
- A controlled one-variable experiment matrix.
- A rerunnable baseline metric runner.
- Per-question retrieval measurements.
- Baseline Hit Rate@3, Recall@3, and MRR results.

The Day 9 workflow is:

​```text
Frozen Baseline Configuration
          ↓
Five Weak Retrieval Questions
          ↓
Baseline Retrieval
          ↓
Failure Analysis
          ↓
Controlled Experiment Matrix
          ↓
Baseline Metrics
          ↓
Ready for Day 10 Retrieval Improvements
​```

Day 09 implementation, baseline measurement, failure analysis, and controlled experiment planning completed successfully.

# Day 10 — Implement Advanced Retrieval and Prove Improvement

## Practical Goal

Improve weak retrieval cases using measured retrieval experiments such as query rewriting, Top-K configuration changes, and cross-encoder reranking.

The Day 10 work compares the improved retrieval approaches against the frozen Day 9 baseline, measures retrieval quality and latency, checks for regressions on previously passing questions, and selects the best configuration for the RAG pipeline.

---

## Implementation

### 1. Run Controlled Retrieval Experiments

The Day 9 experiment matrix was used as the starting point for the Day 10 retrieval experiments.

The planned experiments were executed using the frozen baseline configuration and compared against controlled changes to individual retrieval variables.

The experiments included:

| Experiment | Case | Variable Changed | Baseline | Experiment |
|---|---|---|---|---|
| EXP-001 | DQ-001 | Query rewrite | Original query | More specific compromised-account query |
| EXP-002 | DQ-002 | Top-K | 3 | 5 |
| EXP-003 | DQ-005 | Top-K | 3 | 2 |
| EXP-004 | DQ-004 | Top-K | 3 | 5 |
| EXP-005 | DQ-003 | Query rewrite | Original query | More specific developer-focused query |

The experiment runner is implemented in:

​```text
day10_experiments.py
​```

The results are stored in:

​```text
day10_experiment_results.json
​```

For each experiment, the implementation records the retrieved documents, expected document rank, Hit@K, Recall@K, and Reciprocal Rank.

### 2. Implement Query Rewriting

A reusable query rewriting component was implemented in:

​```text
query_rewriter.py
​```

The component generates a clearer search query while preserving the original question's meaning and avoiding unsupported assumptions.

The query rewriting experiments are implemented in:

​```text
day10_query_rewrite_experiment.py
​```

The results are stored in:

​```text
day10_query_rewrite_results.json
​```

The query rewrite experiment improved the compromised-account retrieval case by moving the expected document DOC-007 from rank 3 to rank 2.

The second query rewrite case retained the expected document DOC-017 at rank 1 without regression.

### 3. Implement Cross-Encoder Reranking

A cross-encoder reranking component was implemented in:

​```text
reranker.py
​```

The retrieval pipeline in `retrieve.py` was updated to retrieve a larger candidate set and then rerank the candidates before selecting the final evidence.

The final retrieval flow is:

​```text
User Question
      ↓
Vector Search — Top 5 Candidates
      ↓
Cross-Encoder Reranking
      ↓
Final Top 3 Results
      ↓
Grounded Generation
​```

The reranking experiment is implemented in:

​```text
day10_reranking_experiment.py
​```

The results are stored in:

​```text
day10_reranking_results.json
​```

Both the original vector distance and the cross-encoder reranking score are preserved so that the effect of reranking can be analyzed.

The reranking experiment successfully improved the compromised-account case:

​```text
Before reranking:
DOC-015 → DOC-012 → DOC-007
                         Rank 3

After reranking:
DOC-007 → DOC-012 → DOC-015
Rank 1
​```

### 4. Select the Best Retrieval Configuration

The evaluated approaches were compared against the frozen Day 9 baseline.

The selected configuration uses:

- Vector search candidate Top-K: `5`
- Cross-encoder reranking: enabled
- Final Top-K: `3`
- Cross-encoder model: `cross-encoder/ms-marco-MiniLM-L6-v2`

The selected configuration is documented in:

​```text
day10_final_config.yaml
​```

The selected approach was preferred because it improved ranking quality while maintaining the retrieval coverage of the baseline configuration.

Approaches that did not provide sufficient evidence of improvement were not selected as the final retrieval configuration.

### 5. Run Full Retrieval Regression Testing

A full regression test was implemented in:

​```text
day10_regression_test.py
​```

The test evaluates the complete 10-question retrieval test set using both the frozen baseline and the selected reranking configuration.

The detailed results are stored in:

​```text
day10_regression_results.json
​```

The recorded regression results show:

| Metric | Baseline | After Reranking |
|---|---:|---:|
| Hit Rate@3 | 1.000 | 1.000 |
| Recall@3 | 1.000 | 1.000 |
| MRR | 0.933 | **1.000** |

The final verification run also recorded an average latency increase of approximately `0.1365 seconds`.

The regression test confirmed that previously passing questions continued to retrieve their expected documents within the Top-3 results.

### 6. Before-and-After Analysis

The complete retrieval comparison is documented in:

​```text
day10_before_after_retrieval_report.md
​```

The report includes:

- Per-question retrieval comparisons
- Baseline and improved retrieval metrics
- Query rewriting results
- Reranking results
- Top-K experiment results
- Regression analysis
- Latency impact
- Rejected approaches
- Selected retrieval configuration
- End-to-end retrieval and generation verification

---

## Day 10 Required Deliverables

| Deliverable | Status |
|---|---|
| At least two retrieval improvements or experiments | Completed |
| Selected retrieval configuration used by the RAG pipeline | Completed |
| Before-and-after retrieval metric report | Completed |
| Regression results for the complete retrieval question set | Completed |

---

## Day 10 Completion Gate

| Requirement | Result |
|---|---|
| Selected approach shows a measured retrieval gain | PASS |
| Previously passing questions checked for regression | PASS |
| Latency impact recorded | PASS |
| Complexity/trade-off of the selected approach recorded | PASS |
| Final retrieval configuration documented | PASS |

---

## Day 10 End-of-Day Evidence

### Improved Retrieval Case

The compromised-account question was used to demonstrate a measurable retrieval improvement:

​```text
Question:
What should an employee do if their account is suspected to be compromised?
​```

The frozen baseline ranked the expected document DOC-007 at rank 3.

After cross-encoder reranking, DOC-007 moved to rank 1.

This demonstrates an improvement in retrieval ranking for a previously weak case.

### Rejected Experiment

The Day 10 experiments also included Top-K and query-rewriting variations that did not provide sufficient evidence of improvement.

These approaches were evaluated against the baseline and documented as rejected or non-selected approaches rather than being treated as improvements without supporting measurements.

This demonstrates that the final configuration was selected based on measured retrieval behavior rather than assumptions.

---

## Day 10 Final Outcome

Day 10 successfully improved the retrieval pipeline using controlled experimentation and cross-encoder reranking.

The selected retrieval flow is:

​```text
Frozen Day 9 Baseline
        ↓
Vector Search — Top 5 Candidates
        ↓
Cross-Encoder Reranking
        ↓
Final Top 3 Results
        ↓
Grounded Generation
​```

The selected configuration improved Mean Reciprocal Rank from **0.933 to 1.000** while maintaining a **1.000 Hit Rate@3** and **1.000 Recall@3** on the complete regression test set.

The final retrieval configuration and supporting experiment evidence are documented in the Day 10 configuration, experiment result files, regression results, and before-and-after retrieval report.

**Day 10 implementation, retrieval improvement experiments, regression validation, and configuration selection completed successfully.**

# DAY 11 — Build FastAPI Service Contracts and Core Endpoints

## Practical Goal

Expose ingestion and question answering through a maintainable FastAPI service with validated request and response models.

The objective of Day 11 was to expose the existing document ingestion and Retrieval-Augmented Generation (RAG) pipeline through a FastAPI service without duplicating the existing pipeline logic.

The API provides the following core endpoints:

- `GET /health`
- `POST /ingest`
- `POST /ask`
- `GET /documents/{id}`

---

## 1. Create the FastAPI Application

A FastAPI application was created under the `api/` package.

The API structure is:

​```text
api/
├── main.py
├── routes.py
├── models.py
└── dependencies.py
​```

### api/main.py

The application entry point:

- Creates the FastAPI application
- Defines API metadata
- Registers the API routes
- Defines the `/health` endpoint
- Uses Pydantic response models for API contracts

The application was successfully started using Uvicorn.

​```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
​```

### api/routes.py

The route module contains the four required API endpoints.

The route handlers are kept thin by reusing the existing RAG modules.

The ingestion endpoint calls:

​```text
ingest_documents()
​```

from the existing ingestion pipeline.

The question-answering endpoint calls:

​```text
answer_question()
​```

from the existing cited RAG pipeline.

This avoids duplicating document processing, retrieval, reranking, and answer-generation logic inside the API layer.

### api/dependencies.py

This module provides configuration and dependency readiness checks.

It checks:

- Generation model configuration
- Vector store availability

Sensitive configuration values such as API keys are not returned by the health endpoint.

---

## 2. Define Pydantic Request and Response Models

The API contracts are defined in `api/models.py`.

### AskRequest

​```python
class AskRequest(BaseModel):
    question: str
    category: str | None = None
    max_distance: float | None = None
​```

This model accepts:

- `question` — required question
- `category` — optional category filter
- `max_distance` — optional retrieval distance threshold

### IngestRequest

​```python
class IngestRequest(BaseModel):
    file_path: str
​```

This model accepts the document file path to be processed.

### IngestResponse

​```python
class IngestResponse(BaseModel):
    document_id: str
    chunk_count: int
    status: str
​```

This response returns:

- Document ID
- Number of chunks created
- Processing status

### DocumentResponse

​```python
class DocumentResponse(BaseModel):
    document_id: str
    title: str
    source_path: str
    updated_at: float
    category: str
    chunk_count: int
    status: str
​```

This response returns stored document metadata and processing status.

### HealthResponse

​```python
class HealthResponse(BaseModel):
    status: str
    dependencies: dict[str, str]
​```

This response returns service status and non-sensitive dependency readiness.

---

## 3. Implement GET /health

### Purpose

The `/health` endpoint checks whether the API service dependencies are ready.

The endpoint checks:

- Generation model readiness
- Vector store readiness

### Endpoint

​```text
GET /health
​```

### Example Response

​```json
{
  "status": "healthy",
  "dependencies": {
    "generation_model": "ready",
    "vector_store": "ready"
  }
}
​```

The endpoint does not expose secrets or internal exception details.

---

## 4. Implement POST /ingest

### Purpose

The `/ingest` endpoint accepts a validated document path and invokes the existing ingestion pipeline.

The existing ingestion flow performs:

​```text
Document
    ↓
Cleaning
    ↓
Chunking
    ↓
Embedding Generation
    ↓
Vector Index Creation
​```

The API route reuses this existing pipeline rather than duplicating the processing logic.

### Endpoint

​```text
POST /ingest
​```

### Example Request

​```json
{
  "file_path": "documents/engineering/DOC-016_software_development_lifecycle.md"
}
​```

### Example Response

​```json
{
  "document_id": "DOC-016",
  "chunk_count": 25,
  "status": "processed"
}
​```

### Error Handling

If the document does not exist:

​```text
404 Document file not found.
​```

If the supplied file is not a Markdown document:

​```text
400 Only Markdown documents are supported.
​```

---

## 5. Implement POST /ask

### Purpose

The `/ask` endpoint accepts a question and optional retrieval filters and sends the request through the existing cited RAG pipeline.

### Endpoint

​```text
POST /ask
​```

### Example Request

​```json
{
  "question": "What is the goal of the software development lifecycle?",
  "category": null,
  "max_distance": null
}
​```

### Example Response

​```json
{
  "answer": "...",
  "sources": [
    "DOC-016:engineering\\DOC-016_software_development_lifecycle.md"
  ],
  "chunks": [
    "..."
  ],
  "scores": [
    1.0751402378082275,
    1.247380018234253,
    1.5933386087417603
  ],
  "status": "answered"
}
​```

The response is validated using the existing `AnswerResponse` Pydantic model.

The response contains:

- Generated answer
- Source references
- Retrieved chunks
- Retrieval scores
- Answer status

---

## 6. Implement GET /documents/{id}

### Purpose

The `/documents/{id}` endpoint returns stored document metadata and processing status.

### Endpoint

​```text
GET /documents/{id}
​```

### Example Request

​```text
GET /documents/DOC-016
​```

### Example Response

​```json
{
  "document_id": "DOC-016",
  "title": "DOC-016_software_development_lifecycle",
  "source_path": "engineering\\DOC-016_software_development_lifecycle.md",
  "updated_at": 1789054023.2216163,
  "category": "engineering",
  "chunk_count": 25,
  "status": "processed"
}
​```

### Not Found Handling

If an unknown document ID is requested, the API returns:

​```text
404 Document not found.
​```

---

## 7. OpenAPI Documentation

FastAPI automatically generates OpenAPI documentation for the API.

The interactive Swagger UI was successfully loaded at:

​```text
http://127.0.0.1:8000/docs
​```

The generated documentation displays the implemented endpoints and their request and response schemas.

The following schemas were verified:

- AskRequest
- IngestRequest
- IngestResponse
- DocumentResponse
- HealthResponse
- AnswerResponse

---

## 8. API Examples

The following examples were used during Day 11 API verification.

### Health Check

​```text
GET /health
​```

​```json
{
  "status": "healthy",
  "dependencies": {
    "generation_model": "ready",
    "vector_store": "ready"
  }
}
​```

### Document Ingestion

​```text
POST /ingest
​```

​```json
{
  "file_path": "documents/engineering/DOC-016_software_development_lifecycle.md"
}
​```

Response:

​```json
{
  "document_id": "DOC-016",
  "chunk_count": 25,
  "status": "processed"
}
​```

### Question Answering

​```text
POST /ask
​```

​```json
{
  "question": "What is the goal of the software development lifecycle?",
  "category": null,
  "max_distance": null
}
​```

Response:

​```json
{
  "answer": "...",
  "sources": [
    "DOC-016:engineering\\DOC-016_software_development_lifecycle.md"
  ],
  "chunks": [
    "..."
  ],
  "scores": [
    1.0751402378082275,
    1.247380018234253,
    1.5933386087417603
  ],
  "status": "answered"
}
​```

### Document Metadata

​```text
GET /documents/DOC-016
​```

Response:

​```json
{
  "document_id": "DOC-016",
  "title": "DOC-016_software_development_lifecycle",
  "source_path": "engineering\\DOC-016_software_development_lifecycle.md",
  "updated_at": 1789054023.2216163,
  "category": "engineering",
  "chunk_count": 25,
  "status": "processed"
}
​```

---

## 9. Day 11 Verification Evidence

The FastAPI application was started successfully using Uvicorn.

​```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
​```

Swagger UI was successfully opened and used for endpoint testing.

### Endpoint Verification

| Endpoint | Test Performed | Result |
|---|---|---|
| GET /health | Valid request | 200 OK |
| POST /ingest | Valid Markdown document | 200 OK |
| POST /ask | Valid question with grounded answer | 200 OK |
| GET /documents/DOC-016 | Existing document ID | 200 OK |

### /health Verification

The endpoint returned:

​```json
{
  "status": "healthy",
  "dependencies": {
    "generation_model": "ready",
    "vector_store": "ready"
  }
}
​```

This confirms that the required generation model configuration and vector store were ready.

### /ingest Verification

The document:

​```text
documents/engineering/DOC-016_software_development_lifecycle.md
​```

was successfully processed.

The API returned:

​```json
{
  "document_id": "DOC-016",
  "chunk_count": 25,
  "status": "processed"
}
​```

### /ask Verification

The following question was successfully processed:

​```text
What is the goal of the software development lifecycle?
​```

The endpoint returned:

​```text
status: answered
​```

The response included the DOC-016 source reference, retrieved chunks, and retrieval scores.

### /documents/DOC-016 Verification

The document metadata endpoint successfully returned:

- Document ID
- Title
- Source path
- Updated timestamp
- Category
- Chunk count
- Processing status

The document contained:

- 25 chunks
- `status: processed`

### Invalid Request Validation

Request validation was also tested by sending an `/ask` request without the required question field.

Request:

​```json
{
  "category": null,
  "max_distance": null
}
​```

The API correctly rejected the request with:

​```text
422 Unprocessable Entity
​```

The validation response identified:

​```text
question
Field required
​```

This confirms that Pydantic/FastAPI validation rejects invalid requests before they reach the RAG pipeline.

---

## 10. Day 11 Completion Gate

| Requirement | Status |
|---|---|
| Runnable FastAPI application | Completed |
| GET /health | Completed |
| POST /ingest | Completed |
| POST /ask | Completed |
| GET /documents/{id} | Completed |
| Pydantic request models | Completed |
| Pydantic response models | Completed |
| OpenAPI documentation loads | Verified |
| Valid requests return expected response shape | Verified |
| Invalid requests rejected by validation | Verified |
| Existing ingestion pipeline reused | Verified |
| Existing RAG pipeline reused | Verified |
| Clear not-found response | Implemented |
| Non-sensitive health response | Implemented |

---

## 11. Day 11 Final Outcome

Day 11 successfully exposed the existing document ingestion and cited RAG question-answering functionality through a maintainable FastAPI service.

The implementation provides:

- Validated API request and response contracts
- Document ingestion through the existing ingestion pipeline
- Grounded question answering through the existing RAG pipeline
- Document metadata retrieval
- Service and dependency readiness checks
- OpenAPI/Swagger documentation
- Request validation and HTTP error handling

The API layer remains separate from the core RAG implementation and reuses the existing pipeline components without duplicating their logic.

**DAY 11 COMPLETED **

All Day 11 implementation, endpoint testing, validation checks, OpenAPI verification, API examples, and completion-gate requirements have been completed successfully.

# DAY 12 — Add SQL Observability, Error Handling, and API Tests

## Practical Goal

Make the FastAPI service diagnosable by recording request IDs, request timing, model and prompt versions, retrieved sources, outcomes, and error categories while providing consistent and safe API error responses.

The objective of Day 12 was to add SQL-based observability to the existing FastAPI service, implement structured error handling, review blocking operations in the API execution path, and create repeatable API tests for successful and failure scenarios.

---

## Implementation

### 1. Create SQL Observability Tables

A dedicated SQL observability package was created under the `observability/` directory.

The structure is:

```text
observability/
├── __init__.py
├── database.py
├── observability_models.py
├── logging_service.py
└── init_db.py
```

#### `observability/database.py`

This module configures the SQLite database using SQLAlchemy.

The database is stored locally as: `observability.db`

The module provides:
- SQLAlchemy engine configuration
- Database session factory
- Base class for ORM models
- Database session dependency

SQLite is configured with:

```python
check_same_thread=False
```

so that database access can safely be used by the FastAPI service execution model.

#### `observability/observability_models.py`

Two SQL tables were created.

**RequestLog**

The `request_logs` table records request-level observability information.

The table stores:
- Request ID
- Endpoint
- Request start time
- Total latency
- Model version
- Prompt version
- Outcome
- Error category

The request ID is unique and indexed so that an API request can be traced efficiently.

**RetrievedSource**

The `retrieved_sources` table stores the sources selected during question answering.

The table stores:
- Request ID
- Source ID
- Retrieval score

The request ID links retrieved source records to their corresponding request log.

The relationship is:

```text
RequestLog
    request_id
        ├────────────── RetrievedSource
        ├────────────── RetrievedSource
        └────────────── RetrievedSource
```

#### `observability/logging_service.py`

A logging service was implemented to perform the database operations required for request observability.

The service provides functions for:
- `create_request_log()`
- `create_retrieved_source_logs()`
- `update_request_log()`

The request lifecycle is recorded as:

```text
Request Started
      ↓
Request Log Created
      ↓
RAG Processing
      ↓
Retrieved Sources Recorded
      ↓
Latency Calculated
      ↓
Outcome Recorded
      ↓
Request Log Updated
```

#### `observability/init_db.py`

This module initializes the observability database tables.

The resulting SQLite database contains:
- `request_logs`
- `retrieved_sources`

The database was verified using SQLite database inspection.

---

### 2. Add Request IDs and Structured Request Logging

The `/ask` endpoint was updated to generate a unique request ID for every request.

A UUID is generated when the request begins:

```text
request_id = <UUID>
```

The same request ID is:
- Returned in the `/ask` API response
- Stored in the `request_logs` table
- Used to associate retrieved source records with the request

This provides request-level traceability across the API response and SQL observability records.

The `/ask` request records:
- Request ID
- Endpoint
- Started At
- Latency
- Model Version
- Prompt Version
- Outcome
- Error Category

The model version is taken from `GENERATION_MODEL` and the prompt version is taken from `PROMPT_VERSION`.

The current configured values are:
- Generation model: `gpt-4.1-mini`
- Prompt version: `v1`

Retrieved sources and their scores are stored separately in the `retrieved_sources` table.

> Sensitive request content and API keys are not stored in the observability tables.

---

### 3. Extend the API Response with Request IDs

The existing `AnswerResponse` model was updated to include:

```python
request_id: str | None = None
```

The response continues to provide:
- `answer`
- `sources`
- `chunks`
- `scores`
- `status`

and now also provides:
- `request_id`

An example successful response is:

```json
{
  "request_id": "c56eb747-29eb-4607-8ee7-6a52a0309646",
  "answer": "...",
  "sources": [
    "DOC-016:engineering\\DOC-016_software_development_lifecycle.md"
  ],
  "chunks": [
    "..."
  ],
  "scores": [
    1.22895419597626
  ],
  "status": "answered"
}
```

The request ID allows the returned API response to be connected directly to its SQL observability records.

---

### 4. Implement Consistent API Error Responses

A structured error response model was added to `api/models.py`.

The model is:

```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    request_id: str | None = None
```

A custom provider error was also added in `api/errors.py`:

```python
class ProviderError(Exception):
    """Raised when an external AI/provider service fails."""
```

The FastAPI application now provides centralized error handlers for different failure categories.

The supported error categories include:

| Error | HTTP Status | Error Code |
|---|---|---|
| Invalid request | 422 | `VALIDATION_ERROR` |
| Invalid document | 400 | `INVALID_DOCUMENT` |
| Document not found | 404 | `DOCUMENT_NOT_FOUND` |
| Missing evidence | 200 | `insufficient_evidence` |
| AI provider failure | 502 | `PROVIDER_ERROR` |
| Internal application failure | 500 | `INTERNAL_ERROR` |

The API returns safe messages rather than exposing internal exception details or stack traces.

For example, a provider failure returns:

```json
{
  "error_code": "PROVIDER_ERROR",
  "message": "The AI provider is temporarily unavailable.",
  "request_id": null
}
```

Internal provider exception details are not returned to the API consumer.

---

### 5. Handle AI Provider Failures Safely

The generation function in `generate.py` was updated to catch provider exceptions and convert them into the application-level `ProviderError`.

The generation request uses the configured OpenRouter provider and `gpt-4.1-mini`.

A maximum generation output limit was also configured:

```python
max_tokens=1000
```

This prevents the provider request from requesting an unnecessarily large maximum output.

The generation flow is:

```text
Grounded Prompt
      ↓
OpenRouter
      ↓
gpt-4.1-mini
      ↓
Generated Answer
```

If the provider fails, the internal exception is converted to `ProviderError`, which is handled by the FastAPI error handler and returned as `502 PROVIDER_ERROR` without exposing provider-specific internal details.

---

### 6. Review Blocking and Async Execution

The API execution path was reviewed to ensure that the existing RAG and database operations do not require asynchronous model or database clients.

The `/ask` route uses the existing synchronous RAG pipeline: `answer_question()`

The route is implemented as a synchronous FastAPI endpoint, allowing FastAPI/Starlette to execute the synchronous endpoint work using its threadpool execution model rather than requiring the synchronous RAG operations to run directly on the async event loop.

The existing ingestion and document metadata routes also use synchronous execution because they call synchronous file and pipeline operations.

The existing RAG implementation remains unchanged in its core processing flow:

```text
Retrieval
    ↓
Reranking
    ↓
Evidence Check
    ↓
Grounded Prompt
    ↓
Generation
    ↓
Citation Validation
```

The Day 12 work therefore focuses on making the API execution and observability layer compatible with the existing synchronous RAG implementation without duplicating or redesigning the core pipeline.

---

### 7. Create API Test Suite

A dedicated API test suite was created under:

```text
tests/
└── test_api.py
```

The tests use FastAPI's `TestClient` and isolate the heavy retrieval dependency during test collection while retaining the real generation configuration.

The test suite covers six required API scenarios:

| Test | Scenario |
|---|---|
| `test_invalid_ask_request` | Invalid `/ask` request |
| `test_unknown_document` | Unknown document ID |
| `test_missing_evidence` | Question with insufficient evidence |
| `test_successful_ask` | Successful question answering |
| `test_provider_failure` | Simulated provider dependency failure |
| `test_successful_ingestion` | Successful document ingestion |

The tests verify both HTTP behavior and the structured response contracts.

---

### 8. Run API Tests

The complete API test suite can be executed with one command:

```bash
python -m pytest tests/test_api.py -v
```

The final verification result was:

```text
6 passed in 5.85s
```

The test results were:

```text
test_invalid_ask_request       PASSED
test_unknown_document          PASSED
test_missing_evidence          PASSED
test_successful_ask            PASSED
test_provider_failure          PASSED
test_successful_ingestion      PASSED
```

This confirms that the required successful, validation, not-found, missing-evidence, provider-failure, and ingestion scenarios are covered by the API test suite.

---

### 9. Successful End-to-End `/ask` Verification

A real question from the existing 10-question evaluation dataset was used for end-to-end API verification.

**Question:**
> What should be considered during the planning stage before implementation begins?

**Expected document:** `DOC-016`

The API returned:
- `request_id`: `c56eb747-29eb-4607-8ee7-6a52a0309646`
- `status`: `answered`

The response identified the source: `DOC-016:engineering\DOC-016_software_development_lifecycle.md`

The request was processed through the existing RAG pipeline:

```text
Question
    ↓
FastAPI /ask
    ↓
Retrieval
    ↓
Cross-Encoder Reranking
    ↓
Evidence Check
    ↓
Grounded Prompt
    ↓
OpenRouter / gpt-4.1-mini
    ↓
Citation Validation
    ↓
AnswerResponse
```

The successful request was also recorded in the SQL observability database.

The corresponding `request_logs` record contained:
- Request ID: `c56eb747-29eb-4607-8ee7-6a52a0309646`
- Endpoint: `/ask`
- Model Version: `gpt-4.1-mini`
- Prompt Version: `v1`
- Outcome: `answered`

The request latency was recorded as approximately: `19237.64 ms`

The corresponding `retrieved_sources` record contained:
- Source: `DOC-016:engineering\DOC-016_software_development_lifecycle.md`
- Score: `1.22895419597626`

This demonstrates that the successful API response can be traced to its request-level and retrieved-source observability records.

---

### 10. Failed End-to-End `/ask` Verification

An unanswerable question was used to verify the missing-evidence behavior:

**Question:**
> What is the annual revenue of the company in 2035?

The API correctly abstained instead of generating an unsupported answer.

The API returned:
- `request_id`: `7e1bdc9c-58e4-4260-a274-8ada5c68143b`
- `status`: `insufficient_evidence`

The response was:
> Insufficient evidence to answer the question from the provided documents.

The response contained no selected sources, chunks, or scores.

The corresponding SQL observability record contained:
- Request ID: `7e1bdc9c-58e4-4260-a274-8ada5c68143b`
- Endpoint: `/ask`
- Model Version: `gpt-4.1-mini`
- Prompt Version: `v1`
- Outcome: `insufficient_evidence`
- Error Category: `missing_evidence`

The recorded latency was approximately: `1124.64 ms`

This demonstrates that an insufficient-evidence request is recorded separately from a successful request and receives the appropriate error category.

---

### 11. Day 12 Required Deliverables

| Deliverable | Status |
|---|---|
| SQL request logging tables | Completed |
| Retrieved source logging | Completed |
| Request ID generation and response traceability | Completed |
| Model and prompt version logging | Completed |
| Latency logging | Completed |
| Structured API error models | Completed |
| Provider failure handling | Completed |
| Safe error responses without stack traces | Completed |
| API/integration test suite | Completed |
| Successful ingestion test | Completed |
| Successful `/ask` test | Completed |
| Invalid input test | Completed |
| Unknown document test | Completed |
| Missing evidence test | Completed |
| Simulated dependency failure test | Completed |
| README test command | Documented |

---

### 12. Day 12 Completion Gate

| Requirement | Result |
|---|---|
| API tests pass with one command | PASS |
| Every `/ask` response is traceable by request ID | PASS |
| Request latency stored | PASS |
| Selected sources and scores stored | PASS |
| Prompt version stored | PASS |
| Model version stored | PASS |
| Request outcome stored | PASS |
| Error category stored for failed request | PASS |
| Internal stack traces exposed to API consumer | PASS |
| Successful request verified end-to-end | PASS |
| Failed request verified end-to-end | PASS |
| Successful and failed SQL records matched to request IDs | PASS |

---

### 13. Day 12 End-of-Day Evidence

#### Successful Request

The following real evaluation question was used:
> What should be considered during the planning stage before implementation begins?

The API returned:
- `request_id`: `c56eb747-29eb-4607-8ee7-6a52a0309646`
- `status`: `answered`

The response was grounded in: `DOC-016:engineering\DOC-016_software_development_lifecycle.md`

The corresponding SQL records stored:
- Model: `gpt-4.1-mini`
- Prompt: `v1`
- Outcome: `answered`
- Latency: `19237.64 ms`
- Retrieved source: `DOC-016:engineering\DOC-016_software_development_lifecycle.md`
- Score: `1.22895419597626`

#### Failed Request

The following unanswerable question was used:
> What is the annual revenue of the company in 2035?

The API returned:
- `request_id`: `7e1bdc9c-58e4-4260-a274-8ada5c68143b`
- `status`: `insufficient_evidence`

The corresponding SQL record stored:
- Model: `gpt-4.1-mini`
- Prompt: `v1`
- Outcome: `insufficient_evidence`
- Error category: `missing_evidence`
- Latency: `1124.64 ms`

The failed request did not generate a source record because no sufficient evidence was selected.

These two examples demonstrate that both successful and unsuccessful `/ask` requests are traceable through request IDs and SQL observability records.

---

### 14. Day 12 Final Outcome

Day 12 successfully added SQL-based observability, structured error handling, provider failure handling, request traceability, and repeatable API testing to the FastAPI service.

The final request observability flow is:

```text
API Request
    ↓
Generate Request ID
    ↓
Create Request Log
    ↓
Execute Existing RAG Pipeline
    ↓
Record Retrieved Sources and Scores
    ↓
Calculate Latency
    ↓
Record Outcome and Error Category
    ↓
Return Structured API Response
```

The API now provides request-level traceability through:
- Request ID
- Latency
- Model Version
- Prompt Version
- Outcome
- Error Category
- Retrieved Sources
- Retrieved Scores

The API test suite completed successfully with:

```text
6 passed in 5.85s
```

Both a successful grounded request and an insufficient-evidence request were verified end-to-end and matched to their corresponding SQL observability records.

**DAY 12 COMPLETED**

All Day 12 implementation, SQL observability, request tracing, error handling, provider failure handling, API testing, end-to-end verification, and completion-gate requirements have been completed successfully.

# DAY 13 — Create the Golden Evaluation Dataset and Runner

## Practical Goal

Build a representative 25-case golden evaluation dataset and a repeatable evaluation runner for measuring the end-to-end quality of the RAG application.

The objective of Day 13 was to define a structured evaluation case format, create a representative golden dataset covering different question types, review the dataset against the approved document corpus, build an automated evaluation runner, and generate timestamped machine-readable evaluation results.

---

## Implementation

### 1. Define the Evaluation Case Format

A structured evaluation case format was created for the golden dataset.

Each case contains:

- `case_id`
- `question`
- `category`
- `expected_source_ids`
- `answerable`
- `expected_facts` where applicable
- `answer_notes` where applicable

The evaluation cases are stored in:

```text
evaluation/
└── golden_set.jsonl
```

Each line in the JSONL file represents one independent evaluation case.

The `expected_source_ids` field identifies the document or documents that should provide evidence for an answerable question.

The `answerable` field indicates whether the question can be answered using the approved document corpus.

---

### 2. Create the 25-Case Golden Dataset

A 25-case golden evaluation dataset was created using the same approved document corpus used by the RAG application.

The dataset contains all required evaluation categories:

| Category | Number of Cases |
|---|---|
| Answerable | 5 |
| Unanswerable | 5 |
| Ambiguous | 5 |
| Multi-document | 5 |
| Adversarial | 5 |
| **Total** | **25** |

The dataset therefore provides coverage for:

- Direct answerable questions
- Questions without sufficient evidence
- Questions requiring interpretation of the relevant policy or document
- Questions requiring evidence from multiple documents
- Adversarial questions designed to test unsupported assumptions and retrieval weaknesses

Every answerable case contains at least one expected source document.

---

### 3. Review the Golden Dataset

A manual review of the 25-case dataset was performed against the approved document corpus.

The review checked:

- Case IDs and JSONL structure
- Question clarity
- Category assignment
- Expected source document IDs
- Answerability labels
- Expected facts where provided
- Multi-document source coverage
- Adversarial case intent
- Whether each case is useful for evaluating the RAG pipeline

The review findings and dataset observations are documented in:

```text
evaluation/dataset_review.md
```

Several cases were refined during the review to make their evaluation intent and expected evidence clearer.

Examples include:

- **GS-011** — Security incident handling
- **GS-016** — Significant product release and initial rollout

Additional multi-document and ambiguous cases were individually validated against their expected source documents.

---

### 4. Build the Evaluation Runner

A repeatable evaluation runner was implemented in:

```text
evaluation/run_evals.py
```

The runner loads the golden dataset and executes every evaluation case against the `/ask` API.

The runner records the following information for each case:

- Case ID
- Expected evaluation information
- HTTP status
- Generated answer
- Citations
- Retrieved chunks
- Retrieval scores
- Answer status
- Request ID
- Latency
- Errors

The evaluation flow is:

```text
Golden Dataset
      ↓
Load Evaluation Cases
      ↓
Send Question to /ask API
      ↓
Capture API Response
      ↓
Record Answer and Citations
      ↓
Record Retrieval Results
      ↓
Record Status and Latency
      ↓
Save Machine-Readable Results
```

---

### 5. Make Evaluation Runs Reproducible

The evaluation runner uses environment-based configuration for the API endpoint and generation configuration.

The current evaluation configuration includes:

| Configuration | Value |
|---|---|
| API Base URL | `http://127.0.0.1:8000` |
| Generation Model | `gpt-4.1-mini` |
| Prompt Version | `v1` |

Each evaluation run creates a new timestamped JSON result file under:

```text
evaluation/results/
```

The timestamped filename prevents previous evaluation results from being overwritten.

Example:

```text
evaluation_run_20260921_151807_663365.json
```

The result file contains:

- Run timestamp
- Configuration
- Total number of cases
- Expected case information
- Actual API results
- Latency
- Retrieval results
- Status
- Request IDs
- Errors

---

### 6. Execute the 25-Case Evaluation

The complete golden evaluation dataset was executed using:

```bash
python evaluation/run_evals.py
```

The runner loaded all 25 evaluation cases and executed them without manual intervention.

The execution flow reported:

```text
Loaded 25 evaluation cases.
Running GS-001...
Running GS-002...
...
Running GS-025...
Completed 25 evaluation cases.
```

A machine-readable result artifact was generated under:

```text
evaluation/results/
```

A previous evaluation result was preserved, and subsequent runs were written as separate timestamped artifacts.

---

### 7. Evaluation Observations

The final 25-case evaluation provided coverage across answerable, unanswerable, ambiguous, multi-document, and adversarial scenarios.

Several cases were also individually validated during the dataset review.

Examples include:

| Case | Validation |
|---|---|
| GS-011 | Security incident handling returned supporting security sources |
| GS-013 | Expense and procurement information retrieved from both expected documents |
| GS-015 | Lost/stolen device response retrieved the expected security and device-management sources |
| GS-016 | Significant release question retrieved DOC-016 and DOC-021 |
| GS-017 | Travel and expense information retrieved both expected documents |
| GS-018 | Offboarding information retrieved the expected access and device documents |
| GS-019 | Additional-access question retrieved the expected security and access-control documents |
| GS-020 | Individually validated successfully against DOC-011 and DOC-026 |
| GS-024 | Correctly handled the office-supplies vendor exception |
| GS-025 | Retrieved the expected Restricted-data sharing sources |

Two evaluation observations were retained as known cases for future retrieval analysis:

- **GS-020** produced an unexpected `insufficient_evidence` result during the final batch run, although the same question had previously succeeded during individual validation.
- **GS-023** consistently demonstrated a retrieval weakness for the password-sharing/MFA scenario and was retained as a useful adversarial evaluation case.

No dataset modification was made solely to hide these retrieval observations.

---

### 8. Day 13 Required Deliverables

| Deliverable | Status |
|---|---|
| 25-case `golden_set.jsonl` | Completed |
| `run_evals.py` evaluation entry point | Completed |
| Machine-readable evaluation result | Completed |
| Dataset review documentation | Completed |

The main Day 13 artifacts are:

```text
evaluation/
├── golden_set.jsonl
├── dataset_review.md
├── run_evals.py
└── results/
    └── evaluation_run_<timestamp>.json
```

---

### 9. Day 13 Completion Gate

| Requirement | Result |
|---|---|
| All required case categories are represented | PASS |
| Every answerable case names at least one expected source | PASS |
| All 25 cases run without manual intervention | PASS |
| Results include configuration and version information | PASS |

The technical completion gate is satisfied for the Day 13 evaluation dataset and runner.

---

### 10. Day 13 End-of-Day Evidence

#### Dataset Distribution

The final golden dataset contains:

```text
Answerable      : 5
Unanswerable    : 5
Ambiguous       : 5
Multi-document  : 5
Adversarial     : 5
--------------------
Total           : 25
```

#### Dataset Review Correction

During manual dataset review, GS-016 was refined to make the required evidence from both the software development lifecycle and product release process explicit.

Final question:

> What should the team verify before releasing a significant product change to production, and what should they do during the initial rollout?

Expected sources:

- `DOC-016` — Software Development Lifecycle
- `DOC-021` — Product Release Process

The revised case was subsequently validated through the RAG application.

---

### 11. Day 13 Final Outcome

Day 13 successfully established a repeatable evaluation foundation for the RAG application.

The project now contains:

- A 25-case golden evaluation dataset
- Coverage across all required evaluation categories
- Expected source information for answerable cases
- Manual dataset review documentation
- An automated evaluation runner
- Timestamped machine-readable evaluation artifacts
- Configuration and prompt-version information for reproducibility
- Documented retrieval observations for future improvement

The Day 13 evaluation workflow is:

```text
Approved Document Corpus
          ↓
Golden Evaluation Dataset
          ↓
Automated Evaluation Runner
          ↓
FastAPI /ask
          ↓
RAG Retrieval and Generation
          ↓
Answer / Citations / Retrieval Results
          ↓
Timestamped Evaluation Artifact
```

The resulting golden dataset and evaluation artifacts provide the baseline required for the next stage of the roadmap: retrieval and answer grading, scorecard generation, and regression checks.

**DAY 13 COMPLETED**

The Day 13 golden dataset, evaluation runner, dataset review, reproducible result generation, completion-gate requirements, and end-of-day evaluation evidence have been completed.

# DAY 14 — Build Retrieval and Answer Graders, Scorecard, and Regression Checks

## Practical Goal

Build a repeatable evaluation and regression framework for measuring retrieval quality, answer quality, citation correctness, abstention behavior, latency, and overall RAG performance.

The objective of Day 14 was to separate retrieval failures from answer failures, generate a review-friendly per-case report, create a baseline evaluation scorecard, identify the main failure categories, and enforce critical quality thresholds through a one-command regression check.

---

## Implementation

### 1. Build the Retrieval Grader

A dedicated retrieval grader was created in:

```text
evaluation/retrieval_grader.py
```

The retrieval grader evaluates the expected source documents against the sources returned by the RAG pipeline.

The grader calculates:

- Hit@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Expected source IDs
- Retrieved source IDs

The Day 14 retrieval evaluation uses:

```text
Top-K = 3
```

Unanswerable evaluation cases are excluded from retrieval quality calculations because they do not have an expected source that the system is required to retrieve.

The retrieval grader therefore measures retrieval performance only across answerable evaluation cases.

---

### 2. Build the Answer Grader

A dedicated answer grader was created in:

```text
evaluation/answer_grader.py
```

The answer grader checks the generated response against the expected evaluation information.

The checks include:

- Answerability
- Citation presence
- Citation validity
- Required fact coverage
- Correct abstention behavior

The grader also validates whether cited document IDs correspond to the expected evidence for the evaluation case.

This separates answer-generation quality from retrieval quality and makes it possible to identify whether a failed case was caused by retrieval, answer generation, citation handling, or abstention behavior.

---

### 3. Generate the Review-Friendly Per-Case Report

A review report generator was created in:

```text
evaluation/review_report.py
```

The report combines the evaluation results and grader results into a single per-case review artifact.

Each case contains information such as:

- Case ID
- Question
- Expected answerability
- Actual answer status
- Overall PASS or FAIL result
- Expected source IDs
- Retrieved source IDs
- Hit@3
- Recall@3
- MRR
- Answerability result
- Citation presence result
- Citation validity result
- Required fact result
- Abstention result
- Latency
- Failure category

The generated report is saved to:

```text
evaluation/results/review_report.json
```

The report provides a review-friendly view of the complete 25-case evaluation.

---

### 4. Generate the Baseline Evaluation Scorecard

A scorecard generator was created in:

```text
evaluation/scorecard.py
```

The scorecard is generated from the saved evaluation and review results.

The scorecard reports:

- Overall pass rate
- Retrieval Hit@3
- Retrieval Recall@3
- MRR
- Citation presence
- Citation validity
- Required fact coverage
- Abstention accuracy
- Failure categories
- Average latency
- Minimum latency
- Maximum latency
- P95 latency
- Evaluation request count as a cost proxy

The generated scorecard is saved to:

```text
evaluation/results/scorecard.json
```

The scorecard therefore provides a repeatable baseline for comparing future changes to the RAG pipeline.

---

### 5. Baseline Evaluation Scorecard

The Day 14 baseline evaluation was generated from the 25-case golden evaluation run.

The baseline results were:

| Metric | Result |
|---|---:|
| Total cases | 25 |
| Passed cases | 16 |
| Failed cases | 9 |
| Overall pass rate | 64.00% |
| Evaluated answerable cases | 19 |
| Hit@3 | 89.47% |
| Recall@3 | 89.47% |
| MRR | 89.47% |
| Citation presence | 89.47% |
| Citation validity | 84.21% |
| Required fact coverage | 52.63% |
| Abstention accuracy | 92.00% |
| Average latency | 3554.40 ms |
| Minimum latency | 542.35 ms |
| Maximum latency | 27013.61 ms |
| P95 latency | 4437.63 ms |
| Evaluation requests | 25 |

The retrieval metrics were calculated across the 19 answerable cases.

The six intentionally unanswerable cases were excluded from retrieval quality metrics but were included when evaluating abstention behavior.

---

### 6. Identify Failure Categories

The review report classified failed evaluation cases into failure categories.

The baseline evaluation identified the following categories:

| Failure Category | Number of Cases |
|---|---:|
| `FACT_COVERAGE_FAILURE` | 6 |
| `RETRIEVAL_FAILURE` | 2 |
| `CITATION_VALIDITY_FAILURE` | 1 |

The failures were identified from the per-case evaluation report rather than from aggregate metrics alone.

The retrieval failures occurred in:

```text
GS-017
GS-023
```

The citation validity failure occurred in:

```text
GS-020
```

The fact coverage failures occurred in:

```text
GS-011
GS-013
GS-016
GS-018
GS-019
GS-025
```

The failure categorization provides a clear starting point for future RAG quality improvements.

---

### 7. Analyze the Weakest Component

The Day 14 scorecard shows that retrieval performance is stronger than answer completeness.

Retrieval performance:

```text
Hit@3      : 89.47%
Recall@3   : 89.47%
MRR        : 89.47%
```

Answer-related metrics showed lower performance, particularly required fact coverage:

```text
Required fact coverage : 52.63%
Citation validity      : 84.21%
```

The failure report identified:

```text
FACT_COVERAGE_FAILURE     : 6
RETRIEVAL_FAILURE         : 2
CITATION_VALIDITY_FAILURE : 1
```

Therefore, the main weakness identified by the Day 14 baseline is answer completeness and required-fact coverage rather than the overall retrieval ranking performance.

This distinction is important because a case can retrieve the correct source document while the generated answer still fails to include all required facts.

---

### 8. Create Regression Thresholds

A regression checker was created in:

```text
evaluation/regression_check.py
```

The regression checker defines minimum acceptable thresholds for critical evaluation metrics.

The configured thresholds are:

| Metric | Minimum Threshold |
|---|---:|
| Overall pass rate | 60% |
| Hit@3 | 85% |
| Recall@3 | 85% |
| MRR | 85% |
| Citation validity | 80% |
| Abstention accuracy | 90% |

The regression checker reads the saved scorecard and compares the current metrics against these thresholds.

If all thresholds are satisfied, the quality check passes.

If any critical threshold falls below its minimum value, the command exits with a failure status.

---

### 9. Run the One-Command Quality Check

The regression check can be executed with:

```bash
python -m evaluation.regression_check
```

The successful baseline check produced:

```text
DAY 14 - REGRESSION CHECK
----------------------------------------------------------------------

overall_pass_rate            actual=64.00% minimum=60.00% [PASS]
hit_at_3                     actual=89.47% minimum=85.00% [PASS]
recall_at_3                  actual=89.47% minimum=85.00% [PASS]
mrr                          actual=89.47% minimum=85.00% [PASS]
citation_validity_rate       actual=84.21% minimum=80.00% [PASS]
abstention_accuracy          actual=92.00% minimum=90.00% [PASS]

----------------------------------------------------------------------

REGRESSION CHECK PASSED
All critical thresholds are satisfied.
```

The regression check therefore provides a single command for determining whether the current evaluation scorecard satisfies the defined quality gates.

---

### 10. Deliberately Test a Regression Failure

The regression mechanism was deliberately tested by temporarily increasing the Hit@3 threshold from:

```text
85%
```

to:

```text
95%
```

The actual Hit@3 remained:

```text
89.47%
```

Therefore, the deliberately weakened threshold caused the regression check to fail.

The result was:

```text
hit_at_3                     actual=89.47% minimum=95.00% [FAIL]

REGRESSION CHECK FAILED
1 critical threshold(s) were not satisfied.
```

After the test, the threshold was restored to:

```text
"hit_at_3": 0.85
```

The normal regression check was then executed again and passed.

This confirms that the regression checker can detect a deliberately broken quality threshold.

---

### 11. Day 14 Evaluation Artifacts

The Day 14 evaluation framework contains the following artifacts:

```text
evaluation/
├── golden_set.jsonl
├── dataset_review.md
├── run_evals.py
├── retrieval_grader.py
├── answer_grader.py
├── review_report.py
├── scorecard.py
├── regression_check.py
└── results/
    ├── evaluation_run_<timestamp>.json
    ├── review_report.json
    └── scorecard.json
```

The main Day 14 artifacts are:

| Artifact | Purpose |
|---|---|
| `retrieval_grader.py` | Measures retrieval quality |
| `answer_grader.py` | Measures answer, citation, fact, and abstention quality |
| `review_report.py` | Generates per-case evaluation and failure details |
| `scorecard.py` | Generates the baseline evaluation scorecard |
| `regression_check.py` | Performs one-command quality threshold validation |
| `review_report.json` | Stores per-case review results |
| `scorecard.json` | Stores the baseline scorecard |

---

## Day 14 Required Deliverables

| Deliverable | Status |
|---|---|
| Retrieval and answer grader modules | Completed |
| Baseline evaluation scorecard | Completed |
| Per-case failure report | Completed |
| Regression thresholds and one-command quality check | Completed |

The Day 14 evaluation framework provides separate retrieval and answer grading, automated scorecard generation, failure categorization, and regression protection.

---

## Day 14 Completion Gate

| Requirement | Result |
|---|---|
| Retrieval and answer failures are reported separately | PASS |
| The scorecard is generated automatically from run results | PASS |
| At least the top three failure categories are identified | PASS |
| A deliberately weakened configuration triggers a regression failure | PASS |

The Day 14 technical completion gate is satisfied.

---

## Day 14 End-of-Day Evidence

### Baseline Scorecard

The final Day 14 baseline scorecard reported:

```text
Overall pass rate     : 64.00%
Hit@3                 : 89.47%
Recall@3              : 89.47%
MRR                   : 89.47%
Citation validity     : 84.21%
Required fact coverage: 52.63%
Abstention accuracy   : 92.00%
```

### Weakest Component

The weakest component identified from the evaluation report was answer completeness, specifically required fact coverage.

The evidence was:

```text
FACT_COVERAGE_FAILURE       : 6 cases
RETRIEVAL_FAILURE           : 2 cases
CITATION_VALIDITY_FAILURE   : 1 case
```

The retrieval metrics remained comparatively strong at 89.47% for Hit@3, Recall@3, and MRR.

This indicates that the primary quality gap in the Day 14 baseline is generated-answer fact coverage rather than basic retrieval ranking.

---

## Day 14 Evaluation Workflow

```text
Golden Evaluation Dataset
        ↓
End-to-End Evaluation Run
        ↓
Retrieval Grader
        +
Answer Grader
        ↓
Per-Case Review Report
        ↓
Baseline Scorecard
        ↓
Failure Category Analysis
        ↓
Regression Threshold Check
        ↓
PASS / FAIL Quality Gate
```

The Day 14 workflow converts the existing Day 13 evaluation runner into a measurable quality framework with retrieval metrics, answer checks, failure analysis, scorecard generation, and regression protection.

---

## Day 14 Final Outcome

Day 14 successfully established a repeatable evaluation and regression framework for the RAG application.

The project now contains:

- Retrieval quality grading
- Answer quality grading
- Hit@3, Recall@3, and MRR metrics
- Citation presence and validity checks
- Required fact coverage checks
- Abstention accuracy checks
- Per-case failure reporting
- Failure category classification
- Baseline evaluation scorecard
- Latency measurements
- Cost proxy measurement
- Regression quality thresholds
- One-command regression validation
- Deliberate regression failure testing

The Day 14 baseline provides a measurable reference point for future improvements to the RAG application.

**DAY 14 COMPLETED**

The Day 14 retrieval and answer graders, baseline scorecard, per-case failure report, failure categorization, regression thresholds, one-command quality check, completion-gate requirements, and end-of-day evaluation evidence have been completed.