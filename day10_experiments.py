import json
from pathlib import Path

from semantic_search import search_chunks


MATRIX_FILE = Path("day9_experiment_matrix.json")
OUTPUT_FILE = Path("day10_experiment_results.json")

BASELINE_TOP_K = 3


def calculate_retrieval_metrics(
    results,
    expected_document_id,
    top_k
):
    retrieved_document_ids = [
        result["document_id"]
        for result in results
    ]

    expected_rank = None

    for rank, document_id in enumerate(
        retrieved_document_ids,
        start=1
    ):
        if document_id == expected_document_id:
            expected_rank = rank
            break

    hit_at_k = expected_rank is not None
    recall_at_k = 1 if hit_at_k else 0

    if expected_rank is not None:
        reciprocal_rank = 1 / expected_rank
    else:
        reciprocal_rank = 0.0

    return {
        "retrieved_documents": [
            {
                "rank": rank,
                "document_id": result["document_id"],
                "distance": result["distance"]
            }
            for rank, result in enumerate(results, start=1)
        ],
        "expected_document_rank": expected_rank,
        f"hit_at_{top_k}": hit_at_k,
        f"recall_at_{top_k}": recall_at_k,
        "reciprocal_rank": reciprocal_rank
    }


# Load the Day 9 experiment matrix
with MATRIX_FILE.open(
    "r",
    encoding="utf-8"
) as file:
    matrix = json.load(file)


experiments = matrix["experiments"]

print(f"Loaded {len(experiments)} Day 10 experiments")


experiment_results = []


for experiment in experiments:

    experiment_id = experiment["experiment_id"]
    case_id = experiment["case_id"]
    question = experiment["question"]
    expected_document_id = None

    # The expected document is stored in the Day 9 weak-question file.
    with open(
        "day9_weak_questions.json",
        "r",
        encoding="utf-8"
    ) as file:
        weak_questions_data = json.load(file)

    for case in weak_questions_data["weak_questions"]:
        if case["case_id"] == case_id:
            expected_document_id = case["expected_document_id"]
            break

    if expected_document_id is None:
        raise ValueError(
            f"Expected document not found for {case_id}"
        )

    primary_variable = experiment["primary_variable"]

    # ---------------------------------------------------------
    # Run baseline
    # ---------------------------------------------------------

    baseline_results = search_chunks(
        question,
        top_k=BASELINE_TOP_K
    )

    baseline_metrics = calculate_retrieval_metrics(
        baseline_results,
        expected_document_id,
        BASELINE_TOP_K
    )

    # ---------------------------------------------------------
    # Run experiment
    # ---------------------------------------------------------

    if primary_variable == "query_rewrite":

        experiment_question = experiment["experiment_value"]
        experiment_top_k = BASELINE_TOP_K

        experiment_results_raw = search_chunks(
            experiment_question,
            top_k=experiment_top_k
        )

    elif primary_variable == "top_k":

        experiment_question = question
        experiment_top_k = experiment["experiment_value"]

        experiment_results_raw = search_chunks(
            experiment_question,
            top_k=experiment_top_k
        )

    else:
        raise ValueError(
            f"Unsupported experiment variable: {primary_variable}"
        )

    experiment_metrics = calculate_retrieval_metrics(
        experiment_results_raw,
        expected_document_id,
        experiment_top_k
    )

    # ---------------------------------------------------------
    # Store result
    # ---------------------------------------------------------

    experiment_result = {
        "experiment_id": experiment_id,
        "case_id": case_id,
        "primary_variable": primary_variable,
        "expected_document_id": expected_document_id,

        "baseline": {
            "question": question,
            "top_k": BASELINE_TOP_K,
            **baseline_metrics
        },

        "experiment": {
            "question": experiment_question,
            "top_k": experiment_top_k,
            **experiment_metrics
        },

        "expected_outcome": experiment["expected_outcome"]
    }

    experiment_results.append(experiment_result)

    # ---------------------------------------------------------
    # Print result
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print(f"Experiment: {experiment_id}")
    print(f"Case: {case_id}")
    print(f"Variable changed: {primary_variable}")
    print(f"Expected document: {expected_document_id}")

    print("\nBaseline:")
    print(
        f"  Retrieved: "
        f"{[r['document_id'] for r in baseline_results]}"
    )
    print(
        f"  Expected rank: "
        f"{baseline_metrics['expected_document_rank']}"
    )
    print(
        f"  Reciprocal Rank: "
        f"{baseline_metrics['reciprocal_rank']:.3f}"
    )

    print("\nExperiment:")
    print(
        f"  Retrieved: "
        f"{[r['document_id'] for r in experiment_results_raw]}"
    )
    print(
        f"  Expected rank: "
        f"{experiment_metrics['expected_document_rank']}"
    )
    print(
        f"  Reciprocal Rank: "
        f"{experiment_metrics['reciprocal_rank']:.3f}"
    )


# Save all experiment results
output_report = {
    "day": 10,
    "task": "Retrieval Experiments",
    "baseline_config_file": "baseline_config.yaml",
    "experiment_matrix_file": "day9_experiment_matrix.json",
    "experiments": experiment_results
}


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        output_report,
        file,
        indent=2,
        ensure_ascii=False
    )


print("\n" + "=" * 60)
print(
    f"Day 10 experiment results saved to {OUTPUT_FILE}"
)