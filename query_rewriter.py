import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
GENERATION_MODEL = os.getenv("GENERATION_MODEL")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


QUERY_REWRITE_PROMPT = """
You are a query rewriting assistant for a document retrieval system.

Rewrite the user's question into a clearer search query that is more suitable
for retrieving relevant information from documents.

Rules:
- Preserve the original meaning.
- Do not add information that the user did not provide.
- Do not assume a specific technology, company, person, platform, or solution.
- Do not answer the question.
- Keep the rewritten query concise.
- Return only the rewritten query.

Original user question:
{question}
"""


def rewrite_query(question):
    prompt = QUERY_REWRITE_PROMPT.format(
        question=question
    )

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    rewritten_query = response.choices[0].message.content.strip()

    return rewritten_query


if __name__ == "__main__":
    question = input("Enter your question: ")

    rewritten_query = rewrite_query(question)

    print("\nOriginal query:")
    print(question)

    print("\nRewritten query:")
    print(rewritten_query)