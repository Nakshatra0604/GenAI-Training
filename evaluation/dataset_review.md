# Day 13 — Golden Dataset Review

## 1. Purpose

This document records the manual review of the Day 13 golden evaluation dataset used to evaluate the end-to-end RAG application.

The purpose of the review was to verify that the evaluation cases are representative of the approved document corpus and that each case has a clear expected source, answerability label, and evaluation intent.

---

## 2. Dataset Details

|    Property       |        Details                       |
|-------------------|--------------------------------------|
| Dataset file      | `evaluation/golden_set.jsonl`        |
| Total cases       | 25                                   |
| Source corpus     | Approved application document corpus |
| Format            | JSON Lines (`.jsonl`)                |
| Evaluation runner | `evaluation/run_evals.py`            |
| Evaluation method | API-based end-to-end evaluation      |
| Generation model  | `gpt-4.1-mini`                       |
| Prompt version    | `v1`                                 |

Each evaluation case contains the following fields:

- `case_id`
- `question`
- `category`
- `expected_source_ids`
- `answerable`
- `expected_facts` (where applicable)
- `answer_notes` (where applicable)

---

## 3. Dataset Distribution

The 25 evaluation cases are distributed across the required categories as follows:

|   Category     | Number of Cases |
|----------------|-----------------|
| Answerable     | 5               |
| Unanswerable   | 5               |
| Ambiguous      | 5               |
| Multi-document | 5               |
| Adversarial    | 5               |
| **Total**      | **25**          |

All required Day 13 evaluation categories are represented.

---

## 4. Review Criteria

The dataset was manually reviewed using the following criteria:

1. Each case has a unique and traceable case ID.
2. Each question is based on the approved document corpus.
3. Answerable cases identify at least one expected source document.
4. Unanswerable cases represent information that should not be supported by the available corpus.
5. Ambiguous cases require the system to identify the relevant policy or document context.
6. Multi-document cases require information from more than one source where appropriate.
7. Adversarial cases test whether the system avoids unsupported conclusions or incorrect assumptions.
8. Expected source IDs were checked against the intended document content.
9. Expected facts and answer notes were included where they provide useful guidance for evaluation.
10. Questions were reviewed for clarity and practical relevance to the application.

---

## 5. Dataset Review Findings

The review confirmed that the dataset provides coverage of different RAG evaluation scenarios rather than testing only straightforward answerable questions.

The dataset includes:

- Direct questions with clearly identifiable source documents.
- Questions where the required information is not available in the corpus.
- Questions involving potentially ambiguous policy areas.
- Questions requiring information from multiple documents.
- Adversarial questions designed to test whether the system follows the available evidence instead of making unsupported assumptions.

The expected source IDs were checked against the corresponding approved documents, and the answerability labels were reviewed based on whether the required information is supported by the corpus.

---

## 6. Cases Refined During Review

### GS-011 — Security Incident Handling

The original case was reviewed and refined to make the expected security-related sources and answerability clearer.

Final question:

> What should I do if I suspect a security problem?

Expected sources:

- `DOC-012` — Incident Response Procedure
- `DOC-015` — Security Awareness Training Guide

The final case was validated through the application and returned an answer supported by the expected security documents.

---

### GS-016 — Significant Product Release

The case was refined to make the required evidence more explicit and to ensure that the evaluation tests information from both the software development lifecycle and product release process.

Final question:

> What should the team verify before releasing a significant product change to production, and what should they do during the initial rollout?

Expected sources:

- `DOC-016` — Software Development Lifecycle
- `DOC-021` — Product Release Process

The final case was validated through the application and retrieved information from both expected documents.

---

## 7. Additional Validation Observations

Several multi-document and ambiguous cases were individually validated during the review to confirm that their expected sources were appropriate.

Examples include:

- `GS-013` — business expenses and purchase requests
- `GS-015` — lost or stolen company device
- `GS-017` — business travel and related expenses
- `GS-018` — employee offboarding and system/device access
- `GS-019` — additional system access and security requirements
- `GS-020` — third-party vendor security requirements
- `GS-025` — sharing Restricted data with an external customer

These cases were checked against the corresponding source documents and retained in the golden dataset.

---

## 8. Known Evaluation Observations

### GS-020 — Third-Party Vendor Security

`GS-020` was successfully validated individually against the expected vendor and information-security documents.

During the final 25-case evaluation run, however, the case returned `insufficient_evidence` without retrieved citations.

A subsequent diagnostic attempt could not be completed because the OpenRouter free-model daily embedding quota had been exhausted.

Therefore, no change was made to the golden question based on this result. The case remains in the dataset for further validation when the embedding service is available.

---

### GS-023 — Password Sharing and MFA

`GS-023` consistently produced insufficient evidence during individual testing, including after natural wording variations.

The case was retained intentionally as a known retrieval weakness because it represents a useful adversarial evaluation scenario and highlights an area where retrieval may require further improvement.

---

## 9. Review Conclusion

The Day 13 golden dataset contains 25 cases covering all required evaluation categories.

The dataset was manually reviewed for:

- source correctness,
- answerability,
- question clarity,
- category coverage,
- multi-document coverage,
- adversarial coverage, and
- evaluation usefulness.

The dataset is suitable for repeatable end-to-end evaluation of the current RAG pipeline.

Known retrieval observations such as `GS-020` and `GS-023` have been retained rather than removed so that they can be used as measurable evaluation cases for future retrieval improvements.

---

## 10. Review Status

**Dataset review status:** Completed

**Dataset size:** 25 cases

**Required categories:** Covered

**Answerable cases with expected sources:** Verified

**Golden dataset:** `evaluation/golden_set.jsonl`

**Evaluation runner:** `evaluation/run_evals.py`

**Result artifacts:** `evaluation/results/`

**Next step:** Use the reviewed golden dataset as the baseline input for Day 14 grading, scorecard generation, and regression evaluation.