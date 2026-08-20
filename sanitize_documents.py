from pathlib import Path
import re

# Defining the input and output folders

INPUT_DIR = Path("raw_documents")
OUTPUT_DIR = Path("documents")

# Creating directory for output files

OUTPUT_DIR.mkdir(exist_ok = True)

# Finding all Markdown files

md_files = list(INPUT_DIR.rglob("*.md"))
print(f"Found {len(md_files)} Markdown files.")

# Sensitive-data patterns

SSN_PATTERN = r"\b\d{3}-\d{2}-\d{4}\b"

PASSWORD_PATTERN = r"(?i)(password\s*:\s*)\S+"

ACCOUNT_PATTERN = r"(?i)(account\s*(?:number|no.?)\s*:\s*)[\d-]+"

ROUTING_PATTERN = r"(?i)(routing\s*(?:number|no.?)\s*:\s*)\d+"

# Process every Markdown file

for file_path in md_files:
    text = file_path.read_text(encoding="utf-8")

    # Redact sensitive values

    text = re.sub(SSN_PATTERN, "[REDACTED]", text)
    text = re.sub(PASSWORD_PATTERN, r"\1[REDACTED]", text)
    text = re.sub(ACCOUNT_PATTERN, r"\1[REDACTED]", text)
    text = re.sub(ROUTING_PATTERN, r"\1[REDACTED]", text)

    # Preserve the original folder structure

    relative_path = file_path.relative_to(INPUT_DIR)
    output_path = OUTPUT_DIR / relative_path

    # Create the required subfolder

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the sanitized document

    output_path.write_text(text, encoding="utf-8")