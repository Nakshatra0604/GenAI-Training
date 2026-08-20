from pathlib import Path
import json


INPUT_DIR = Path("cleaned_documents")
OUTPUT_FILE = Path("chunks.jsonl")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

md_files = list(INPUT_DIR.rglob("*.md"))

print(f"Found {len(md_files)} cleaned Markdown files")


def create_chunks(text: str) -> list[str]:

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - CHUNK_OVERLAP

    return chunks


def split_by_headings(text: str) -> list[str]:

    sections = []
    current_section = []

    for line in text.splitlines():

        if line.startswith("#") and line.lstrip().startswith("#"):

            if current_section:
                sections.append(
                    "\n".join(current_section).strip()
                )
                current_section = []

        current_section.append(line)

    if current_section:
        sections.append(
            "\n".join(current_section).strip()
        )

    return [section for section in sections if section]


all_chunks = []


for file_path in md_files:

    text = file_path.read_text(encoding="utf-8")

    relative_path = file_path.relative_to(INPUT_DIR)

    document_id = file_path.stem.split("_")[0]

    title = file_path.stem

    updated_at = file_path.stat().st_mtime

    category = (
        relative_path.parts[0]
        if len(relative_path.parts) > 1
        else "general"
    )

    sections = split_by_headings(text)

    # Start chunk numbering from 0 for each document
    chunk_index = 0

    for section in sections:

        if len(section) <= CHUNK_SIZE:
            section_chunks = [section]
        else:
            section_chunks = create_chunks(section)

        for chunk in section_chunks:

            record = {
                "chunk_id": f"{document_id}_{chunk_index}",
                "document_id": document_id,
                "title": title,
                "source_path": str(relative_path),
                "updated_at": updated_at,
                "chunk_index": chunk_index,
                "category": category,
                "text": chunk
            }

            all_chunks.append(record)

            chunk_index += 1


# Save chunks as JSONL

with OUTPUT_FILE.open("w", encoding="utf-8") as file:

    for record in all_chunks:
        file.write(
            json.dumps(record, ensure_ascii=False) + "\n"
        )


print(f"Created {len(all_chunks)} chunks.")
print(f"Saved chunks to {OUTPUT_FILE}")