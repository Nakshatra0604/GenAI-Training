import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

GOLDEN_SET_PATH = PROJECT_ROOT / "evaluation" / "golden_set.jsonl"


# Common words that do not carry much meaning when comparing facts.
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "must",
    "of",
    "on",
    "or",
    "should",
    "that",
    "the",
    "their",
    "this",
    "to",
    "with",
    "when",
    "will",
    "would",
}


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file into a list of dictionaries."""
    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def load_golden_set() -> dict[str, dict]:
    """Load the golden dataset indexed by case ID."""
    golden_records = load_jsonl(GOLDEN_SET_PATH)

    return {
        record["case_id"]: record
        for record in golden_records
    }


def load_latest_evaluation_result() -> tuple[Path, list[dict]]:
    """Load the most recent saved evaluation result."""
    results_dir = PROJECT_ROOT / "evaluation" / "results"

    result_files = sorted(
        results_dir.glob("evaluation_run_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not result_files:
        raise FileNotFoundError(
            "No evaluation result files were found in evaluation/results."
        )

    latest_file = result_files[0]

    with latest_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return latest_file, data["results"]


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower()

    # Normalize common number formats.
    text = text.replace("$", " dollar ")
    text = text.replace("%", " percent ")

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize_meaningful_words(text: str) -> set[str]:
    """
    Convert text into meaningful normalized tokens.

    Stopwords are removed so that fact comparison focuses
    on important content words.
    """
    normalized = normalize_text(text)

    tokens = normalized.split()

    return {
        token
        for token in tokens
        if token not in STOPWORDS
    }


def check_answerability(
    expected_answerable: bool,
    actual_status: str,
) -> bool:
    """
    Check whether the system returned the expected answerability status.
    """
    expected_status = (
        "answered"
        if expected_answerable
        else "insufficient_evidence"
    )

    return actual_status == expected_status


def extract_citation_source_ids(
    citations: list[str],
) -> list[str]:
    """
    Extract document IDs from citation strings.

    Example:
        DOC-009:it\\DOC-009_software_installation_request_process.md

    becomes:
        DOC-009
    """
    source_ids = []

    for citation in citations:
        if not citation:
            continue

        match = re.search(r"(DOC-\d+)", citation)

        if match:
            source_ids.append(match.group(1))

    return source_ids


def check_citation_presence(
    answerable: bool,
    citations: list[str],
) -> bool:
    """
    Check whether citations are present.

    Answerable questions should contain at least one citation.

    For intentionally unanswerable questions, citation presence
    is not required because the expected behavior is abstention.
    """
    if not answerable:
        return True

    return len(citations) > 0


def check_citation_validity(
    answerable: bool,
    citations: list[str],
    expected_sources: list[str],
) -> bool:
    """
    Check whether the generated citations point to expected
    supporting documents.

    At least one cited document must match one of the expected
    source IDs.
    """
    if not answerable:
        return True

    if not citations:
        return False

    cited_source_ids = set(
        extract_citation_source_ids(citations)
    )

    expected_source_ids = set(expected_sources)

    return bool(cited_source_ids & expected_source_ids)


def fact_is_supported(
    fact: str,
    answer: str,
    minimum_coverage: float = 0.60,
) -> bool:
    """
    Determine whether an expected fact is reasonably represented
    in the generated answer.

    This uses normalized meaningful-word overlap rather than exact
    sentence matching because generated answers can legitimately
    paraphrase the golden facts.
    """
    fact_tokens = tokenize_meaningful_words(fact)
    answer_tokens = tokenize_meaningful_words(answer)

    if not fact_tokens:
        return True

    matched_tokens = fact_tokens & answer_tokens

    coverage = len(matched_tokens) / len(fact_tokens)

    return coverage >= minimum_coverage


def check_required_facts(
    answerable: bool,
    answer: str,
    expected_facts: list[str],
) -> dict:
    """
    Check whether required facts are represented in the answer.
    """
    if not answerable:
        return {
            "required_facts_available": False,
            "required_facts_total": 0,
            "required_facts_found": 0,
            "required_facts_missing": [],
            "required_facts_pass": True,
        }

    if not expected_facts:
        return {
            "required_facts_available": False,
            "required_facts_total": 0,
            "required_facts_found": 0,
            "required_facts_missing": [],
            "required_facts_pass": True,
        }

    missing_facts = []

    for fact in expected_facts:
        if not fact_is_supported(
            fact=fact,
            answer=answer,
        ):
            missing_facts.append(fact)

    found_count = len(expected_facts) - len(missing_facts)

    return {
        "required_facts_available": True,
        "required_facts_total": len(expected_facts),
        "required_facts_found": found_count,
        "required_facts_missing": missing_facts,
        "required_facts_pass": len(missing_facts) == 0,
    }


def check_correct_abstention(
    expected_answerable: bool,
    actual_status: str,
) -> bool:
    """
    Check whether the system correctly answered or abstained.
    """
    if expected_answerable:
        return actual_status == "answered"

    return actual_status == "insufficient_evidence"


def grade_case(
    golden_case: dict,
    evaluation_result: dict,
) -> dict:
    """Grade answer quality for one evaluation case."""

    answerable = golden_case.get("answerable", False)

    expected_sources = golden_case.get(
        "expected_source_ids",
        [],
    )

    expected_facts = golden_case.get(
        "expected_facts",
        [],
    )

    actual = evaluation_result.get("actual", {})

    answer = actual.get("answer", "")
    status = actual.get("status", "")

    # IMPORTANT:
    # The evaluation JSON uses "citations", not "sources".
    citations = actual.get("citations", [])

    answerability_pass = check_answerability(
        expected_answerable=answerable,
        actual_status=status,
    )

    citation_presence_pass = check_citation_presence(
        answerable=answerable,
        citations=citations,
    )

    citation_validity_pass = check_citation_validity(
        answerable=answerable,
        citations=citations,
        expected_sources=expected_sources,
    )

    required_facts_result = check_required_facts(
        answerable=answerable,
        answer=answer,
        expected_facts=expected_facts,
    )

    abstention_pass = check_correct_abstention(
        expected_answerable=answerable,
        actual_status=status,
    )

    answer_pass = (
        answerability_pass
        and citation_presence_pass
        and citation_validity_pass
        and required_facts_result["required_facts_pass"]
        and abstention_pass
    )

    return {
        "case_id": evaluation_result["case_id"],
        "answerable": answerable,
        "actual_status": status,
        "answerability_pass": answerability_pass,
        "citation_presence_pass": citation_presence_pass,
        "citation_validity_pass": citation_validity_pass,
        "required_facts_pass": required_facts_result[
            "required_facts_pass"
        ],
        "required_facts_available": required_facts_result[
            "required_facts_available"
        ],
        "required_facts_total": required_facts_result[
            "required_facts_total"
        ],
        "required_facts_found": required_facts_result[
            "required_facts_found"
        ],
        "required_facts_missing": required_facts_result[
            "required_facts_missing"
        ],
        "correct_abstention_pass": abstention_pass,
        "answer_pass": answer_pass,
        "expected_sources": expected_sources,
        "actual_citations": citations,
        "actual_citation_source_ids": extract_citation_source_ids(
            citations
        ),
    }


def grade_evaluation_run(
    evaluation_results: list[dict],
    golden_cases: dict[str, dict],
) -> dict:
    """Grade answer quality for the complete evaluation run."""

    case_results = []

    for evaluation_result in evaluation_results:
        case_id = evaluation_result["case_id"]

        golden_case = golden_cases.get(case_id)

        if not golden_case:
            continue

        case_grade = grade_case(
            golden_case=golden_case,
            evaluation_result=evaluation_result,
        )

        case_results.append(case_grade)

    total_cases = len(case_results)

    if total_cases == 0:
        return {
            "total_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "answer_pass_rate": 0.0,
            "citation_presence_rate": 0.0,
            "citation_validity_rate": 0.0,
            "abstention_accuracy": 0.0,
            "required_facts_pass_rate": 0.0,
            "required_fact_cases": 0,
            "cases": [],
        }

    passed_cases = sum(
        case["answer_pass"]
        for case in case_results
    )

    answerable_cases = [
        case
        for case in case_results
        if case["answerable"]
    ]

    citation_presence_count = sum(
        case["citation_presence_pass"]
        for case in answerable_cases
    )

    citation_validity_count = sum(
        case["citation_validity_pass"]
        for case in answerable_cases
    )

    abstention_count = sum(
        case["correct_abstention_pass"]
        for case in case_results
    )

    required_fact_cases = [
        case
        for case in case_results
        if case["required_facts_available"]
    ]

    required_fact_pass_count = sum(
        case["required_facts_pass"]
        for case in required_fact_cases
    )

    return {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": total_cases - passed_cases,
        "answer_pass_rate": passed_cases / total_cases,
        "citation_presence_rate": (
            citation_presence_count / len(answerable_cases)
            if answerable_cases
            else 0.0
        ),
        "citation_validity_rate": (
            citation_validity_count / len(answerable_cases)
            if answerable_cases
            else 0.0
        ),
        "abstention_accuracy": (
            abstention_count / total_cases
        ),
        "required_facts_pass_rate": (
            required_fact_pass_count / len(required_fact_cases)
            if required_fact_cases
            else 0.0
        ),
        "required_fact_cases": len(required_fact_cases),
        "cases": case_results,
    }


def main():
    print("=" * 70)
    print("DAY 14 - ANSWER GRADER")
    print("=" * 70)

    evaluation_file, evaluation_results = (
        load_latest_evaluation_result()
    )

    golden_cases = load_golden_set()

    print(f"Evaluation run: {evaluation_file.name}")
    print(f"Total evaluation cases: {len(evaluation_results)}")
    print()

    scorecard = grade_evaluation_run(
        evaluation_results=evaluation_results,
        golden_cases=golden_cases,
    )

    print("-" * 70)
    print("ANSWER SCORECARD")
    print("-" * 70)

    print(
        f"Total cases:                  "
        f"{scorecard['total_cases']}"
    )

    print(
        f"Passed cases:                 "
        f"{scorecard['passed_cases']}"
    )

    print(
        f"Failed cases:                 "
        f"{scorecard['failed_cases']}"
    )

    print(
        f"Answer pass rate:             "
        f"{scorecard['answer_pass_rate']:.4f} "
        f"({scorecard['answer_pass_rate'] * 100:.2f}%)"
    )

    print(
        f"Citation presence rate:      "
        f"{scorecard['citation_presence_rate']:.4f} "
        f"({scorecard['citation_presence_rate'] * 100:.2f}%)"
    )

    print(
        f"Citation validity rate:      "
        f"{scorecard['citation_validity_rate']:.4f} "
        f"({scorecard['citation_validity_rate'] * 100:.2f}%)"
    )

    print(
        f"Abstention accuracy:         "
        f"{scorecard['abstention_accuracy']:.4f} "
        f"({scorecard['abstention_accuracy'] * 100:.2f}%)"
    )

    print(
        f"Required-facts pass rate:    "
        f"{scorecard['required_facts_pass_rate']:.4f} "
        f"({scorecard['required_facts_pass_rate'] * 100:.2f}%)"
    )

    print(
        f"Cases with required facts:   "
        f"{scorecard['required_fact_cases']}"
    )

    print()
    print("-" * 70)
    print("PER-CASE ANSWER RESULTS")
    print("-" * 70)

    for case in scorecard["cases"]:
        print(
            f"{case['case_id']} | "
            f"Expected answerable: {case['answerable']} | "
            f"Actual: {case['actual_status']} | "
            f"Answerability: "
            f"{'PASS' if case['answerability_pass'] else 'FAIL'} | "
            f"Citation presence: "
            f"{'PASS' if case['citation_presence_pass'] else 'FAIL'} | "
            f"Citation validity: "
            f"{'PASS' if case['citation_validity_pass'] else 'FAIL'} | "
            f"Facts: "
            f"{'PASS' if case['required_facts_pass'] else 'FAIL'} | "
            f"Abstention: "
            f"{'PASS' if case['correct_abstention_pass'] else 'FAIL'} | "
            f"OVERALL: "
            f"{'PASS' if case['answer_pass'] else 'FAIL'}"
        )

        if case["required_facts_missing"]:
            print(
                f"    Missing facts: "
                f"{case['required_facts_missing']}"
            )

        if not case["answer_pass"]:
            print(
                f"    Expected sources: "
                f"{case['expected_sources']}"
            )

            print(
                f"    Actual citation source IDs: "
                f"{case['actual_citation_source_ids']}"
            )


if __name__ == "__main__":
    main()