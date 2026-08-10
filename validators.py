import json
import os
from datetime import datetime


from pydantic import ValidationError

from models.summarization_model import SummarizationOutput
from models.extraction_model import ExtractionOutput
from models.classification_model import ClassificationOutput

def log_validation_failure(task, error_message, raw_output):

    log_file = os.path.join("logs", "validation_failures.json")

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "failure_type": "validation_error",
        "task": task,
        "reason": error_message,
        "raw_output": raw_output
    }

    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as file:
                logs = json.load(file)

                if not isinstance(logs, list):
                    logs = []
        else:
            logs = []

    except (json.JSONDecodeError, FileNotFoundError):
        logs = []

    logs.append(log_entry)

    with open(log_file, "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=4)

VALID_TASKS = [
    "summarization",
    "extraction",
    "classification"
]

VALID_SAMPLE_TYPES = [
    "normal",
    "representative",
    "long",
    "ambiguous",
    "incomplete",
    "malformed",
    "empty"
]


def validate_input(task, sample_type, sample_text):

    if task not in VALID_TASKS:
        return False, "Invalid task."

    if sample_type not in VALID_SAMPLE_TYPES:
        return False, "Invalid sample type."

    if not sample_text.strip():
        return False, "Input text is empty."

    return True, None

def parse_summarization(response_text):

    bullets = []

    for line in response_text.splitlines():

        line = line.strip()

        if line.startswith("-"):
            bullets.append(line[1:].strip())

    return {
        "summary_points": bullets
    }


def parse_extraction(response_text):

    data = {}

    for line in response_text.splitlines():

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip().lower().replace(" ", "_")
        value = value.strip()

        if key == "name":
            data["name"] = value

        elif key == "email":
            data["email"] = value

        elif key == "phone_number":
            data["phone_number"] = value

        elif key == "organization":
            data["organization"] = value

    return data


def parse_classification(response_text):

    data = {}

    for line in response_text.splitlines():

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip().lower()
        value = value.strip()

        if key == "label":
            data["label"] = value

        elif key == "reason":
            data["reason"] = value

    return data

def validate_output(task, parsed_data, raw_output):

    try:

        if task == "summarization":
            SummarizationOutput(**parsed_data)

        elif task == "extraction":
            ExtractionOutput(**parsed_data)

        elif task == "classification":
            ClassificationOutput(**parsed_data)

        return True, "Validation Passed"

    except ValidationError as e:
        error_message = str(e)

        log_validation_failure(
            task,
            error_message,
            raw_output
        )

        return False, error_message
