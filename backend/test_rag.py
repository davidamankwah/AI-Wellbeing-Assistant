from app.services.rag_service import retrieve_sources

test_queries = [
    "I'm stressed about my university exams.",
    "I've been feeling lonely at university.",
    "I am having trouble sleeping.",
    "How do I repair a bicycle tyre?"
]

for number, query in enumerate(test_queries, start=1):
    print(f"\nTest {number}")
    print("Query:", query)

    results = retrieve_sources(
        query=query,
        top_k=2,
        verified_only=False
    )

    if not results:
        print("No relevant sources found.")
    else:
        for result in results:
            print("Title:", result.title)
            print("Source:", result.source)
            print("Verified:", result.verified)
            print("Similarity:", result.score)
            print("Content:", result.content)
            print("-" * 40)

    print("=" * 60)


verified_results = retrieve_sources(
    query="university exam stress",
    verified_only=True
)

assert verified_results, "Expected verified sources"

assert all(
    result.verified for result in verified_results
)

print("\nVerified-only filtering test passed!")
