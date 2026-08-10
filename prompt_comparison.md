# Prompt Version Comparison

## Task

Text Classification

## Version 1 Prompt

The V1 prompt instructed the model to:

- Classify the text into exactly one allowed label.
- Choose only one label from Technology, Healthcare, Finance, or Education.
- Provide a one-sentence reason.
- Base the classification on the supplied source text.

## Version 2 Prompt

The V2 prompt kept the same classification instructions but added one meaningful instruction:

> Base your classification on the primary domain the text is about as a whole, not on individual keywords.

## Why the Prompt Was Changed

The change was introduced to improve classification of mixed-domain or malformed inputs where keywords from multiple domains are present.

## Before-and-After Result

### Test Case: CLS_004

The input contained mixed terminology related to education, technology, and finance.

| Version | Predicted Label | Expected Label | Result |
|---------|-----------------|----------------|--------|
| V1      | Education       | Finance        | FAIL   |
| V2      | Finance         | Finance        | PASS   |

### Conclusion

V1 was influenced by the education-related terms in the input and classified the case as Education.

V2 correctly identified the primary domain as Finance after the prompt was updated to consider the text as a whole rather than individual keywords.

Therefore, Version 2 was selected as the preferred prompt version based on the fixed test-case results.