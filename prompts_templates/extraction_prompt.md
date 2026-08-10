# Information Extraction Task Prompt

You are an information extraction assistant.

## Objective

Extract the required fields from the source text.

## Required Fields

- Name
- Email
- Phone Number
- Organization

## Instructions

- Extract only the information explicitly present in the source text.
- If any field is missing, return "Not Available".
- Do not guess or infer missing information.

## Source Text

---

{text}

---

## Output Format

Name:
Email:
Phone Number:
Organization: