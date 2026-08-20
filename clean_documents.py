from pathlib import Path
import re


# Input and output folders

INPUT_DIR = Path("documents")
OUTPUT_DIR = Path("cleaned_documents")

# Create the output directory if it does not exist

OUTPUT_DIR.mkdir(exist_ok=True)


def clean_text(text: str) -> str:
    """
    Normalize whitespace and remove empty Markdown sections
    while preserving meaningful headings and content.
    """

    # Normalize different line-ending formats
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing whitespace from every line
    lines = [line.rstrip() for line in text.split("\n")]

    # Remove excessive blank lines
    cleaned_lines = []
    previous_blank = False

    for line in lines:
        if line.strip() == "":
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
        else:
            cleaned_lines.append(line)
            previous_blank = False

    text = "\n".join(cleaned_lines).strip()

    # Split the document into Markdown sections
    sections = re.split(r"(?=^#{1,6}\s+)", text, flags=re.MULTILINE)

    cleaned_sections = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        lines = section.split("\n")

        # If this is a Markdown heading, check whether
        # there is meaningful content after the heading.
        if re.match(r"^#{1,6}\s+", lines[0]):
            heading = lines[0]
            body = "\n".join(lines[1:]).strip()

            # Keep the section if it has content.
            if body:
                cleaned_sections.append(section)
        else:
            # Keep content that exists before the first heading.
            cleaned_sections.append(section)

    # Join sections with a single blank line
    cleaned_text = "\n\n".join(cleaned_sections)

    return cleaned_text.strip()


# Find all Markdown files recursively

md_files = list(INPUT_DIR.rglob("*.md"))

print(f"Found {len(md_files)} Markdown files.")


# Process every Markdown document

for file_path in md_files:

    # Read the document

    text = file_path.read_text(encoding="utf-8")

    # Clean the document

    cleaned_text = clean_text(text)

    # Preserve the original folder structure

    relative_path = file_path.relative_to(INPUT_DIR)
    output_path = OUTPUT_DIR / relative_path

    # Create the required subfolder

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the cleaned document

    output_path.write_text(cleaned_text, encoding="utf-8")


print(f"Cleaned {len(md_files)} Markdown files.")