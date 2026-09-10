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
├── cleaned_documents/                    # Cleaned document files
├── vector_store/                         # Persistent ChromaDB vector index
│
├── sanitize_documents.py                 # Sanitizes sensitive document values
├── clean_documents.py                    # Loads and cleans document text
├── chunk_documents.py                    # Splits cleaned documents into chunks
├── chunk_quality_review.py               # Performs chunk quality checks
├── chunk_quality_review.md               # Chunk quality review output
├── chunks.jsonl                          # Normalized chunk dataset
│
├── generate_embeddings.py                # Generates and reuses embeddings
├── create_vector_index.py                # Creates the ChromaDB vector index
├── embeddings.jsonl                      # Chunk embeddings and metadata
│
├── semantic_search.py                    # Reusable semantic search function
├── filter_demo.py                        # Metadata-filtered search demonstration
├── retrieval_test_set.json               # Retrieval test questions
├── test_retrieval.py                     # Day 6 retrieval test runner
├── retrieval_results.json                # Retrieval test results
│
├── ingest.py                             # Complete document ingestion pipeline
├── retrieve.py                           # Day 10 retrieval pipeline with reranking
├── generate.py                           # Grounded answer generation pipeline
├── grounded_prompt.py                    # Grounded answer prompt
├── answer_model.py                       # Validated answer response model
├── citation_validator.py                 # Validates answer citations
├── test_pipeline.py                      # Day 7 integration tests
│
├── baseline_config.yaml                  # Frozen Day 9 baseline configuration
├── day9_weak_questions.json              # Five weak retrieval cases
├── day9_failure_analysis.json            # Day 9 retrieval failure analysis
├── day9_experiment_matrix.json           # Controlled Day 9 experiment plan
├── day9_baseline_metrics.py             # Day 9 baseline metric runner
├── day9_baseline_metrics.json            # Day 9 baseline metric results
│
├── query_rewriter.py                     # Reusable query rewriting component
├── day10_experiments.py                  # Executes planned Day 10 experiments
├── day10_experiment_results.json         # Day 10 experiment results
├── day10_query_rewrite_experiment.py    # Query rewriting experiment
├── day10_query_rewrite_results.json      # Query rewriting results
├── reranker.py                            # Cross-encoder reranking component
├── day10_reranking_experiment.py         # Cross-encoder reranking experiment
├── day10_reranking_results.json           # Reranking experiment results
├── day10_regression_test.py               # Full retrieval regression test
├── day10_regression_results.json          # Regression test results
├── day10_before_after_retrieval_report.md # Day 10 before-and-after report
├── day10_final_config.yaml                # Selected Day 10 configuration
│
├── api/                                   # FastAPI service layer
│   ├── main.py                            # FastAPI application entry point
│   ├── routes.py                          # API endpoint definitions
│   ├── models.py                          # Pydantic request and response models
│   └── dependencies.py                    # Configuration and dependency readiness checks
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
