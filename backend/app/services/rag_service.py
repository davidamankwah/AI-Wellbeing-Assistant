
import json
import re
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BACKEND_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_PATH = (
    BACKEND_DIR / "knowledge_base" / "sources.json"
)

# Initial experimental thresholds.
# These must be calibrated using evaluation results.
MIN_SIMILARITY = 0.18
MIN_WORD_SIMILARITY = 0.035

WORD_WEIGHT = 0.60
CHAR_WEIGHT = 0.40

@dataclass
class RetrievedSource:
    id: str
    title: str
    source: str
    url: str | None
    verified: bool
    content: str
    score: float

# Limited, manually defined wellbeing vocabulary.
# This is not a semantic embedding model.
QUERY_EXPANSIONS = {
    "isolated": "lonely loneliness social connection",
    "isolation": "lonely loneliness social connection",
    "friends": "loneliness social connection",
    "overwhelmed": "stress stressed coping",
    "relax": "stress relaxation coping",
    "nervous": "anxiety anxious stress",
    "revision": "exams studying assessment",
    "tired": "sleep sleeping rest",
    "insomnia": "sleep sleeping",
}

WELLBEING_TERMS = {
    "stress", "stressed", "anxiety", "anxious",
    "lonely", "loneliness", "isolated", "isolation",
    "friends", "friendship", "overwhelmed",
    "relax", "relaxation", "nervous",
    "exam", "exams", "revision", "studying",
    "study", "sleep", "sleeping", "insomnia",
    "tired", "wellbeing", "mental", "mood",
    "coping", "support", "depression",
    "sad", "university", "lectures"
}

def load_knowledge_base() -> list[dict]:
    """
    Load and validate local knowledge-base documents.
    """
    with open(
        KNOWLEDGE_BASE_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError(
            "Knowledge base must contain a JSON list."
        )

    required_fields = {
        "id", "title", "source",
        "url", "verified", "content"
    }

    for document in documents:
        if not isinstance(document, dict):
            raise ValueError(
                "Each source must be a JSON object."
            )

        if not required_fields.issubset(document):
            raise ValueError(
                "Knowledge-base source is missing fields."
            )

        if not isinstance(document["content"], str):
            raise ValueError(
                "Source content must be text."
            )

        if not document["content"].strip():
            raise ValueError(
                "Source content cannot be empty."
            )

    return documents

def normalise_text(text: str) -> str:
    """
    Lowercase and normalise whitespace.
    """
    return " ".join(text.lower().split())

def expand_query(query: str) -> str:
    """
    Expand selected wellbeing-related terms.

    Only whole words are matched to avoid accidental
    substring expansion.
    """
    normalised = normalise_text(query)

    words = set(
        re.findall(r"\b[a-z]+\b", normalised)
    )

    additions = []

    for term, expansion in QUERY_EXPANSIONS.items():
        if term in words:
            additions.append(expansion)

    if additions:
        return normalised + " " + " ".join(additions)

    return normalised

def is_potentially_relevant(query: str) -> bool:
    """
    Lightweight relevance gate.

    This is a preliminary filter, not the authoritative
    wellbeing-scope classifier.
    """
    words = set(
        re.findall(r"\b[a-z]+\b", query.lower())
    )

    return bool(words.intersection(WELLBEING_TERMS))

def retrieve_sources(
    query: str,
    top_k: int = 3,
    verified_only: bool = False
) -> list[RetrievedSource]:
    """
    Retrieve relevant local knowledge-base sources.

    Combines word and character TF-IDF similarity,
    with limited query expansion and relevance filtering.

    Does not call an LLM or external service.
    """
    if not isinstance(query, str) or not query.strip():
        return []

    if top_k < 1:
        return []

    # Avoid retrieving wellbeing references for
    # clearly unrelated requests.
    if not is_potentially_relevant(query):
        return []

    documents = load_knowledge_base()

    if verified_only:
        documents = [
            document for document in documents
            if document["verified"] is True
        ]

    if not documents:
        return []

    expanded_query = expand_query(query)

    # Include document titles to improve topic matching.
    document_texts = [
        f"{document['title']} {document['content']}"
        for document in documents
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

    word_documents = word_vectorizer.fit_transform(
        document_texts
    )

    char_documents = char_vectorizer.fit_transform(
        document_texts
    )

    word_query = word_vectorizer.transform(
        [expanded_query]
    )

    char_query = char_vectorizer.transform(
        [expanded_query]
    )

    word_scores = cosine_similarity(
        word_query,
        word_documents
    )[0]

    char_scores = cosine_similarity(
        char_query,
        char_documents
    )[0]

    combined_scores = (
        WORD_WEIGHT * word_scores
        + CHAR_WEIGHT * char_scores
    )

    ranked_indices = combined_scores.argsort()[::-1]

    results = []

    for index in ranked_indices:
        score = float(combined_scores[index])
        word_score = float(word_scores[index])

        # Require both sufficient combined relevance
        # and at least some word-level overlap.
        if score < MIN_SIMILARITY:
            continue

        if word_score < MIN_WORD_SIMILARITY:
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