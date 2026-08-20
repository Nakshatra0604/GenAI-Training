from semantic_search import search_chunks

question = "What is the software development lifecycle?"

results = search_chunks(
    question,
    top_k=3,
    category="engineering"
)

for result in results:
    print(result)