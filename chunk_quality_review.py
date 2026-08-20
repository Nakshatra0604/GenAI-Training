import json
from pathlib import Path


# Input and output configuration

INPUT_FILE = Path("chunks.jsonl")
DOCUMENTS_DIR = Path("cleaned_documents")
REVIEW_FILE = Path("chunk_quality_review.md")


# Load generated chunks

with INPUT_FILE.open("r", encoding="utf-8") as file:
    chunks = [json.loads(line) for line in file if line.strip()]

print(f"Loaded {len(chunks)} chunks.")


# Read the cleaned source documents

documents = []

for file_path in DOCUMENTS_DIR.rglob("*.md"):
    text = file_path.read_text(encoding="utf-8")

    documents.append(
        {
            "source_path": str(file_path.relative_to(DOCUMENTS_DIR)),
            "word_count": len(text.split()),
            "text": text,
        }
    )


# Identify short, long, and structured documents

short_documents = [
    document
    for document in documents
    if 100 <= document["word_count"] <= 300
]

long_documents = [
    document
    for document in documents
    if 2000 <= document["word_count"] <= 4000
]

structured_documents = [
    document
    for document in documents
    if document["text"].count("\n## ") >= 3
    and "|" in document["text"]
]


print(f"Short documents found: {len(short_documents)}")
print(f"Long documents found: {len(long_documents)}")
print(f"Structured documents found: {len(structured_documents)}")


# Show the five longest documents

documents_by_length = sorted(
    documents,
    key=lambda document: document["word_count"],
    reverse=True
)

print("\nFive longest documents:")

for document in documents_by_length[:5]:
    print(
        f"{document['source_path']} "
        f"({document['word_count']} words)"
    )


# Select representative documents

short_document = short_documents[0] if short_documents else None
long_document = long_documents[0] if long_documents else None
structured_document = structured_documents[0] if structured_documents else None


print("\nSelected documents:")

if short_document:
    print(
        f"Short: {short_document['source_path']} "
        f"({short_document['word_count']} words)"
    )
else:
    print("Short: No matching document found.")

if long_document:
    print(
        f"Long: {long_document['source_path']} "
        f"({long_document['word_count']} words)"
    )
else:
    print("Long: No matching document found.")

if structured_document:
    print(
        f"Structured: {structured_document['source_path']} "
        f"({structured_document['word_count']} words)"
    )
else:
    print("Structured: No matching document found.")


# ---------------------------------------------------------
# Quality check 1: Empty chunks
# ---------------------------------------------------------

empty_chunks = [
    chunk
    for chunk in chunks
    if not chunk["text"].strip()
]

print(f"\nEmpty chunks found: {len(empty_chunks)}")


# ---------------------------------------------------------
# Quality check 2: Headings separated from content
# ---------------------------------------------------------

heading_split_issues = []

for index, chunk in enumerate(chunks):

    text = chunk["text"].strip()

    if not text:
        continue

    lines = text.splitlines()

    last_line = lines[-1].strip()

    if (
        last_line.startswith("#")
        and index + 1 < len(chunks)
        and chunks[index + 1]["document_id"] == chunk["document_id"]
    ):
        heading_split_issues.append(
            {
                "chunk": chunk,
                "next_chunk": chunks[index + 1],
            }
        )


print(
    f"Heading/content split issues found: "
    f"{len(heading_split_issues)}"
)


# ---------------------------------------------------------
# Quality check 3: Excessive overlap
# ---------------------------------------------------------

overlap_issues = []

for index in range(len(chunks) - 1):

    current = chunks[index]
    next_chunk = chunks[index + 1]

    if current["document_id"] != next_chunk["document_id"]:
        continue

    current_words = current["text"].split()
    next_words = next_chunk["text"].split()

    if not current_words or not next_words:
        continue

    overlap_count = 0

    for size in range(
        min(150, len(current_words), len(next_words)),
        0,
        -1
    ):
        if current_words[-size:] == next_words[:size]:
            overlap_count = size
            break

    if overlap_count > 100:
        overlap_issues.append(
            {
                "chunk_id": current["chunk_id"],
                "next_chunk_id": next_chunk["chunk_id"],
                "overlap_words": overlap_count,
            }
        )


print(
    f"Excessive overlap issues found: "
    f"{len(overlap_issues)}"
)


# ---------------------------------------------------------
# Find chunks belonging to a selected source document
# ---------------------------------------------------------

def get_document_chunks(source_path):
    return [
        chunk
        for chunk in chunks
        if chunk["source_path"] == source_path
    ]


# Collect representative chunks

review_documents = []

for document_type, document in [
    ("Short", short_document),
    ("Long", long_document),
    ("Structured", structured_document),
]:
    if document:

        document_chunks = get_document_chunks(
            document["source_path"]
        )

        review_documents.append(
            {
                "type": document_type,
                "document": document,
                "chunks": document_chunks,
            }
        )


# ---------------------------------------------------------
# Create review file
# ---------------------------------------------------------

with REVIEW_FILE.open("w", encoding="utf-8") as file:

    file.write("# Chunk Quality Review\n\n")

    file.write("## Review Scope\n\n")

    file.write(
        "This review inspects representative short, long, and "
        "structured documents and their generated chunks.\n\n"
    )

    file.write(
        f"Total source documents processed: "
        f"{len(documents)}\n\n"
    )

    file.write(
        f"Total chunks generated: "
        f"{len(chunks)}\n\n"
    )

    file.write("## Quality Check Results\n\n")

    file.write(
        f"- Empty chunks: {len(empty_chunks)}\n"
    )

    file.write(
        f"- Heading/content split issues: "
        f"{len(heading_split_issues)}\n"
    )

    file.write(
        f"- Excessive overlap issues: "
        f"{len(overlap_issues)}\n\n"
    )

    # Record the chunking issue that was identified and corrected

    file.write("## Chunking Issue Corrected\n\n")

    file.write(
        "During review, chunk indexes were found to restart from 0 "
        "for each Markdown section within the same document. This "
        "caused duplicate chunk IDs such as DOC-017_0. The chunking "
        "logic was corrected so chunk indexes continue sequentially "
        "across the entire document.\n\n"
    )

    file.write("### Before Correction\n\n")

    file.write(
        "- DOC-017_0\n"
        "- DOC-017_0\n"
        "- DOC-017_0\n\n"
    )

    file.write("### After Correction\n\n")

    file.write(
        "- DOC-017_0\n"
        "- DOC-017_1\n"
        "- DOC-017_2\n\n"
    )


    # Representative documents

    for review in review_documents:

        document = review["document"]
        document_chunks = review["chunks"]

        file.write(
            f"## {review['type']} Document\n\n"
        )

        file.write(
            f"**Source:** `{document['source_path']}`  \n"
        )

        file.write(
            f"**Word count:** {document['word_count']}  \n"
        )

        file.write(
            f"**Chunks generated:** "
            f"{len(document_chunks)}\n\n"
        )

        for chunk in document_chunks[:3]:

            file.write(
                f"### Chunk {chunk['chunk_index']}\n\n"
            )

            file.write(
                f"- **Chunk ID:** `{chunk['chunk_id']}`\n"
            )

            # Separate chunk_index metadata field

            file.write(
                f"- **Chunk Index:** `{chunk['chunk_index']}`\n"
            )

            file.write(
                f"- **Document ID:** `{chunk['document_id']}`\n"
            )

            file.write(
                f"- **Title:** `{chunk['title']}`\n"
            )

            file.write(
                f"- **Source Path:** `{chunk['source_path']}`\n"
            )

            file.write(
                f"- **Updated At:** `{chunk['updated_at']}`\n"
            )

            file.write(
                f"- **Category:** `{chunk['category']}`\n\n"
            )

            file.write("**Chunk text:**\n\n")

            file.write("```text\n")
            file.write(chunk["text"])
            file.write("\n```\n\n")


print(
    f"\nReview file created: {REVIEW_FILE}"
)