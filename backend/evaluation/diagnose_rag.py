
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.rag_service import (
    load_knowledge_base,
    expand_query,
    is_potentially_relevant,
    WORD_WEIGHT,
    CHAR_WEIGHT,
    MIN_SIMILARITY,
    MIN_WORD_SIMILARITY
)


QUERIES = [
    "I am having trouble sleeping.",
    "I feel isolated and want to make friends.",
    "I feel overwhelmed and need ways to relax.",
    "Can you recommend a gaming laptop?",
]


def diagnose(query, documents):

    print("\nQUERY:", query)
    print(
        "Relevance gate:",
        is_potentially_relevant(query)
    )
    print("Expanded:", expand_query(query))

    texts = [
        f"{doc['title']} {doc['content']}"
        for doc in documents
    ]

    word_vectorizer = TfidfVectorizer(
        lowercase=True,
        analyzer="word",
        ngram_range=(1, 2),
        stop_words="english",
        sublinear_tf=True
    )

    char_vectorizer = TfidfVectorizer(
        lowercase=True,
        analyzer="char_wb",
        ngram_range=(3, 5),
        sublinear_tf=True
    )

    word_docs = word_vectorizer.fit_transform(texts)
    char_docs = char_vectorizer.fit_transform(texts)

    expanded = expand_query(query)

    word_query = word_vectorizer.transform([expanded])
    char_query = char_vectorizer.transform([expanded])

    word_scores = cosine_similarity(
        word_query, word_docs
    )[0]

    char_scores = cosine_similarity(
        char_query, char_docs
    )[0]

    combined = (
        WORD_WEIGHT * word_scores
        + CHAR_WEIGHT * char_scores
    )

    ranked = combined.argsort()[::-1]

    for index in ranked[:3]:
        word_score = float(word_scores[index])
        char_score = float(char_scores[index])
        combined_score = float(combined[index])

        passes = (
            is_potentially_relevant(query)
            and combined_score >= MIN_SIMILARITY
            and word_score >= MIN_WORD_SIMILARITY
        )

        print(
            f"Source: {documents[index]['title']} | "
            f"Word: {word_score:.4f} | "
            f"Char: {char_score:.4f} | "
            f"Combined: {combined_score:.4f} | "
            f"Passes: {passes}"
        )


def main():

    documents = load_knowledge_base()

    for query in QUERIES:
        diagnose(query, documents)
        print("-" * 70)


if __name__ == "__main__":
    main()
