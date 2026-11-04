
import json
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Resolve paths relative to this file, not the terminal.
BACKEND_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_PATH = BACKEND_DIR / "knowledge_base" / "sources.json"

MIN_SIMILARITY = 0.15


@dataclass
class RetrievedSource:
    id: str
    title: str
    source: str
    url: str | None
    verified: bool
    content: str
    score: float


def load_knowledge_base() -> list[dict]:
    """
    Load local knowledge-base documents.
    """
    with open(
        KNOWLEDGE_BASE_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError("Knowledge base must contain a JSON list.")

    required_fields = {
        "id", "title", "source",
        "url", "verified", "content"
    }

    for document in documents:
        if not isinstance(document, dict):
            raise ValueError("Each source must be a JSON object.")

        if not required_fields.issubset(document):
            raise ValueError("Knowledge-base source is missing fields.")

        if not isinstance(document["content"], str):
            raise ValueError("Source content must be text.")

        if not document["content"].strip():
            raise ValueError("Source content cannot be empty.")

    return documents


def retrieve_sources(
    query: str,
    top_k: int = 3,
    verified_only: bool = False
) -> list[RetrievedSource]:
    """
    Search local documents using TF-IDF similarity.

    Returns relevant passages with source metadata.
    Does not call an LLM or external service.
    """
    if not isinstance(query, str) or not query.strip():
        return []

    if top_k < 1:
        return []

    documents = load_knowledge_base()

    if verified_only:
        documents = [
            doc for doc in documents
            if doc["verified"] is True
        ]

    if not documents:
        return []

    contents = [doc["content"] for doc in documents]

      
    vectorizer = TfidfVectorizer(
        lowercase=True,
        analyzer="char_wb",
        ngram_range=(3, 5),
        sublinear_tf=True
    )

    document_vectors = vectorizer.fit_transform(contents)
    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(
        query_vector,
        document_vectors
    )[0]

    ranked_indices = similarities.argsort()[::-1]

    results = []

    for index in ranked_indices:
        score = float(similarities[index])

        if score < MIN_SIMILARITY:
            continue

        document = documents[index]

        results.append(
            RetrievedSource(
                id=document["id"],
                title=document["title"],
                source=document["source"],
                url=document["url"],
                verified=document["verified"],
                content=document["content"],
                score=round(score, 4)
            )
        )

        if len(results) >= top_k:
            break

    return results
