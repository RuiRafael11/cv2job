import math
import re
from collections import Counter

TOKEN_PATTERN = re.compile(r"(?u)\b[a-zA-Z+#.]{2,}\b")

STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "for", "with", "to", "in", "on", "at", "by", "from",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "should", "could", "may", "might", "must", "can", "of", "as",
    "that", "this", "these", "those", "it", "its", "we", "you", "your", "our", "they",
    "their", "he", "she", "his", "her", "not", "but", "if", "then", "than", "so", "such",
    "de", "da", "do", "dos", "das", "em", "no", "na", "nos", "nas", "para", "com", "por",
    "um", "uma", "uns", "umas", "os", "as", "o", "e", "ou", "se", "ao", "aos", "à", "às",
})


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_PATTERN.findall(text) if t.lower() not in STOPWORDS]


def _document_frequency(docs: list[list[str]]) -> dict[str, int]:
    df: dict[str, int] = {}
    for doc in docs:
        for term in set(doc):
            df[term] = df.get(term, 0) + 1
    return df


def _tfidf_vector(tokens: list[str], df: dict[str, int], n_docs: int) -> dict[str, float]:
    tf = Counter(tokens)
    total = len(tokens) or 1
    vec: dict[str, float] = {}
    for term, count in tf.items():
        idf = math.log((1 + n_docs) / (1 + df.get(term, 0))) + 1
        vec[term] = (count / total) * idf
    return vec


def cosine_similarity_text(a: str, b: str) -> float:
    docs = [tokenize(a), tokenize(b)]
    if not docs[0] or not docs[1]:
        return 0.0
    df = _document_frequency(docs)
    v1 = _tfidf_vector(docs[0], df, 2)
    v2 = _tfidf_vector(docs[1], df, 2)
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    dot = sum(v1[t] * v2[t] for t in common)
    norm1 = math.sqrt(sum(x * x for x in v1.values()))
    norm2 = math.sqrt(sum(x * x for x in v2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def top_job_terms(job: str, cv: str, top_n: int = 40) -> list[str]:
    job_tokens = tokenize(job)
    cv_tokens = tokenize(cv)
    if not job_tokens:
        return []
    df = _document_frequency([job_tokens, cv_tokens])
    job_vec = _tfidf_vector(job_tokens, df, 2)
    return [term for term, _ in sorted(job_vec.items(), key=lambda x: -x[1])[:top_n]]
