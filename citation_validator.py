import re


def extract_source_labels(context):
    """
    Extract complete source labels from the provided context.
    """

    pattern = r"\[Source: (.*?)\]"

    return set(
        re.findall(pattern, context)
    )


def validate_citations(answer, context):
    """
    Validate citations used in the answer
    against the sources supplied in the context.
    """

    valid_sources = extract_source_labels(context)

    # Extract document IDs from the supplied sources
    source_map = {}

    for source in valid_sources:
        document_id = source.split(":", 1)[0]
        source_map[document_id] = source

    # Extract short citations such as [DOC-009]
    citation_pattern = r"\[(DOC-\d+)\]"

    cited_ids = set(
        re.findall(citation_pattern, answer)
    )

    invalid_ids = cited_ids - set(source_map.keys())

    valid_citations = [
        source_map[document_id]
        for document_id in cited_ids
        if document_id in source_map
    ]

    return {
        "valid": len(invalid_ids) == 0 and len(cited_ids) > 0,
        "valid_sources": valid_citations,
        "invalid_sources": list(invalid_ids)
    }