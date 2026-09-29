import re


RESTRICTED_REQUEST_PATTERNS = [
    r"\b(reveal|show|give|provide|list|display|dump|expose|extract)\b.*\b(passwords?|api keys?|tokens?|credentials?)\b",
    r"\b(reveal|show|give|provide|list|display|dump|expose|extract)\b.*\b(ssn|ssns|social security numbers?)\b",   
    r"\b(reveal|show|give|provide|list|display|dump|expose|extract)\b.*\b(account numbers?|routing numbers?)\b",
    r"\b(all|any|every)\b.*\b(passwords?|api keys?|tokens?|credentials?)\b",
    r"\b(all|any|every)\b.*\b(ssn|social security numbers?)\b",
    r"\b(all|any|every)\b.*\b(account numbers?|routing numbers?)\b",
]


def check_content_policy(question: str) -> dict:
    """
    Check application-specific content policy rules.
    """

    if not isinstance(question, str):
        return {
            "allowed": False,
            "control": "content_policy",
            "reason_code": "INVALID_QUESTION_TYPE"
        }

    normalized_question = question.strip().lower()

    if not normalized_question:
        return {
            "allowed": False,
            "control": "content_policy",
            "reason_code": "EMPTY_QUESTION"
        }

    for pattern in RESTRICTED_REQUEST_PATTERNS:
        if re.search(pattern, normalized_question):
            return {
                "allowed": False,
                "control": "content_policy",
                "reason_code": "RESTRICTED_DATA_REQUEST"
            }

    return {
        "allowed": True,
        "control": "content_policy",
        "reason_code": "ALLOWED"
    }