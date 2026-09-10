# DAY 10 — Before/After Retrieval Improvement Report

## 1. Objective

The objective of Day 10 was to improve retrieval quality for weak retrieval cases identified during Day 9 and select a retrieval configuration that provides measurable improvement without introducing regressions in previously passing questions.

The baseline retrieval system used vector similarity search with a fixed `top_k` of 3.

During Day 10, controlled experiments were performed using:

* Query rewriting
* Top-k changes
* Cross-encoder reranking

The final selected configuration was then integrated into the RAG retrieval pipeline and verified through the end-to-end `generate.py` flow.

---

## 2. Baseline Configuration

The Day 9 baseline configuration was frozen before conducting Day 10 experiments.

| Configuration                 | Baseline                          |
| ----------------------------- | --------------------------------- |
| Embedding model               | `nvidia/NemoTron-3-Embed-1B:free` |
| Chunk size                    | 1000                              |
| Chunk overlap                 | 150                               |
| Vector retrieval top-k        | 3                                 |
| Retrieval category filter     | None                              |
| Retrieval distance threshold  | None                              |
| Generation evidence threshold | 0.8 vector distance               |
| Maximum context chunks        | 3                                 |
| Prompt version                | `current_day8`                    |

The frozen configuration is recorded in:

`baseline_config.yaml`

---

## 3. Experiments Performed

### 3.1 Query Rewriting

A reusable query rewriting component was implemented in:

`query_rewriter.py`

The component rewrites the original user question into a concise retrieval-oriented query while preserving the original meaning and avoiding unsupported assumptions.

The query rewriting capability was tested on weak retrieval cases DQ-001 and DQ-003.

### DQ-001 — Compromised Account

**Original question:**

> What should an employee do if their account is suspected to be compromised?

**Rewritten query:**

> What to do if an employee's account is suspected compromised?

**Result:**

The expected document `DOC-007` improved from rank 3 to rank 2.

| Metric                 | Before | After |
| ---------------------- | -----: | ----: |
| Expected document rank |      3 |     2 |
| Reciprocal Rank        |  0.333 | 0.500 |

The experiment demonstrated a measurable improvement, although the expected document did not move to rank 1.

### DQ-003 — Error Handling

**Original question:**

> What is the recommended approach for handling errors in code?

**Rewritten query:**

> error handling best practices in code

**Result:**

`DOC-017` remained rank 1.

The experiment did not improve the expected document's rank, but it did not cause a regression.

---

## 4. Cross-Encoder Reranking

A cross-encoder reranking component was implemented in:

`reranker.py`

Model:

`cross-encoder/ms-marco-MiniLM-L6-v2`

The retrieval process was changed from selecting the top vector results directly to:

```text
User Question
     ↓
Vector Search
     ↓
Top 5 Candidate Chunks
     ↓
Cross-Encoder Reranking
     ↓
Final Top 3 Chunks
```

The original vector distance was preserved in the retrieval results, and the cross-encoder relevance score was recorded separately.

### DQ-001 — Compromised Account

| Metric            | Vector Retrieval | After Reranking |
| ----------------- | ---------------: | --------------: |
| Expected document |          DOC-007 |         DOC-007 |
| Expected rank     |                3 |               1 |
| Reciprocal Rank   |            0.333 |           1.000 |

This was a significant retrieval improvement.

The correct document `DOC-007` moved from rank 3 to rank 1.

### DQ-003 — Error Handling

| Metric            | Vector Retrieval | After Reranking |
| ----------------- | ---------------: | --------------: |
| Expected document |          DOC-017 |         DOC-017 |
| Expected rank     |                1 |               1 |
| Reciprocal Rank   |            1.000 |           1.000 |

The correct document remained at rank 1, so there was no regression.

### DQ-005 — Elevated Access

| Metric            | Vector Retrieval | After Reranking |
| ----------------- | ---------------: | --------------: |
| Expected document |          DOC-014 |         DOC-014 |
| Expected rank     |                1 |               1 |
| Reciprocal Rank   |            1.000 |           1.000 |

The expected document remained rank 1 after reranking.

---

## 5. Top-k Experiments

Top-k changes were also tested as controlled experiments.

### DQ-002 — Planning Stage

The experiment changed:

`top_k: 3 → 5`

`DOC-016` remained rank 1.

The additional results did not produce a measurable ranking improvement because the expected document was already correctly ranked first.

### DQ-005 — Elevated Access

The experiment changed:

`top_k: 3 → 2`

The two relevant `DOC-014` chunks were retained while the less-specific third result was removed.

This demonstrated that reducing the final context size can remove some noisy retrieval results while retaining the relevant evidence.

### DQ-004 — Software Request

The experiment changed:

`top_k: 3 → 5`

The additional results did not provide the missing approval-owner information.

Therefore, increasing top-k was rejected for this case because it did not improve the available evidence.

---

## 6. Full Regression Results

The complete 10-question retrieval test set was used to check whether the selected reranking approach introduced regressions.

### Before Reranking

| Metric          |         Result |
| --------------- | -------------: |
| Hit Rate@3      |          1.000 |
| Recall@3        |          1.000 |
| MRR             |          0.933 |
| Average latency | 0.3332 seconds |

### After Reranking

| Metric          |         Result |
| --------------- | -------------: |
| Hit Rate@3      |          1.000 |
| Recall@3        |          1.000 |
| MRR             |          1.000 |
| Average latency | 0.5064 seconds |

### Overall Change

| Metric          |          Change |
| --------------- | --------------: |
| Hit Rate@3      |       No change |
| Recall@3        |       No change |
| MRR             |   0.933 → 1.000 |
| Average latency | +0.1732 seconds |

The full regression test maintained 100% Hit Rate@3 and Recall@3 while improving MRR from 0.933 to 1.000.

The detailed per-question regression results are stored in:

`day10_regression_results.json`

---

## 7. Key Regression Result

The compromised-account question provides the clearest example of the retrieval improvement.

**Question:**

> What should an employee do if their account is suspected to be compromised?

### Before

```text
Rank 1 — DOC-015
Rank 2 — DOC-012
Rank 3 — DOC-007
```

### After Cross-Encoder Reranking

```text
Rank 1 — DOC-007
Rank 2 — DOC-012
Rank 3 — DOC-015
```

Therefore:

```text
DOC-007: Rank 3 → Rank 1
```

This demonstrates that the reranker improved the ordering of relevant evidence without reducing the overall Hit Rate@3 or Recall@3.

---

## 8. Latency and Complexity Impact

Cross-encoder reranking adds additional inference work because the candidate chunks must be scored against the user question.

Measured average latency increased from:

`0.3332 seconds → 0.5064 seconds`

This represents an average additional latency of approximately:

`0.1732 seconds`

The selected approach therefore trades a small increase in retrieval latency for improved ranking quality.

The implementation also adds an additional model dependency and reranking step to the retrieval pipeline.

---

## 9. Rejected Approaches

### Query Rewriting as the Primary Selected Configuration

Query rewriting produced an improvement for DQ-001:

`Rank 3 → Rank 2`

However, it did not improve DQ-003 and did not provide as strong an overall ranking improvement as cross-encoder reranking.

Therefore, query rewriting was not selected as the primary retrieval improvement.

### Increasing top-k for DQ-004

Increasing top-k from 3 to 5 did not reveal the missing approval-owner information.

Therefore, increasing top-k was rejected for this case.

### Increasing top-k for DQ-002

Increasing top-k from 3 to 5 did not improve the expected document's rank because `DOC-016` was already ranked first.

Therefore, the change provided no meaningful ranking improvement.

---

## 10. Selected Retrieval Configuration

Based on the controlled experiments and full regression results, the selected Day 10 retrieval configuration is:

| Configuration          | Selected Value                        |
| ---------------------- | ------------------------------------- |
| Embedding model        | `nvidia/NemoTron-3-Embed-1B:free`     |
| Vector candidate top-k | 5                                     |
| Reranker               | `cross-encoder/ms-marco-MiniLM-L6-v2` |
| Final retrieval top-k  | 3                                     |
| Category filter        | None                                  |
| Reranking              | Enabled                               |

The selected retrieval flow is:

```text
User Question
      ↓
Vector Search
      ↓
Top 5 Candidate Chunks
      ↓
Cross-Encoder Reranking
      ↓
Final Top 3 Chunks
      ↓
Grounded Generation
```

---

## 11. RAG Pipeline Integration

The selected retrieval configuration was integrated into the existing RAG pipeline through `retrieve.py`.

The current pipeline is:

```text
User Question
      ↓
generate.py
      ↓
retrieve.py
      ↓
semantic_search.py
      ↓
Top 5 Vector Candidates
      ↓
reranker.py
      ↓
Final Top 3 Reranked Chunks
      ↓
Grounded Prompt
      ↓
LLM Generation
      ↓
Citation Validation
      ↓
Final AnswerResponse
```

The existing ingestion flow remains responsible for preparing documents and storing their embeddings, while `retrieve.py` handles query-time retrieval and reranking.

---

## 12. End-to-End Verification

The final selected retrieval configuration was tested through the actual CLI RAG pipeline using:

```bash
python generate.py
```

Test question:

> What should an employee do if their account is suspected to be compromised?

The pipeline returned:

```json
{
  "status": "answered"
}
```

The final response contained evidence from:

* `DOC-007`
* `DOC-012`
* `DOC-015`

The response was grounded in the retrieved document context and passed citation validation.

This confirms that the selected retrieval configuration is not only an isolated experiment but is also connected to the actual RAG question-answering pipeline.

---

## 13. Final Trade-off

The selected cross-encoder reranking approach provides a measurable retrieval-quality improvement:

```text
MRR: 0.933 → 1.000
```

while maintaining:

```text
Hit Rate@3: 1.000
Recall@3: 1.000
```

The primary trade-off is an average latency increase of approximately:

```text
+0.1732 seconds
```

The additional latency and model dependency are accepted because the approach improves ranking quality without causing regression in the tested retrieval set.

---

## 14. Conclusion

Day 10 retrieval experiments demonstrated that cross-encoder reranking provides the strongest measured improvement among the tested approaches.

The final selected configuration uses:

```text
Top 5 vector candidates
        ↓
Cross-Encoder Reranking
        ↓
Final Top 3
```

The configuration was integrated into `retrieve.py` and verified through the end-to-end `generate.py` RAG pipeline.

The detailed experimental and regression evidence is retained in the corresponding JSON result files for auditability.
