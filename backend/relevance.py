"""Pure helpers for converting reranker outputs into citation confidence."""

import math
import re
from typing import Optional


QUERY_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "did", "do",
    "does", "for", "from", "has", "have", "how", "i", "in", "is", "it",
    "of", "on", "or", "the", "their", "to", "was", "what", "when", "where",
    "which", "who", "why", "with", "would", "you", "your",
}


def calibrate_bge_reranker_score(
    raw_score: Optional[float], *, score_is_probability: bool = False
) -> Optional[float]:
    """Convert a BGE reranker score to a conservative 0--1 relevance score.

    BGE rerankers are trained with logits, whose useful relevance boundary is
    approximately 2.0.  A sigmoid value returned by a client library is *not*
    the same thing as a calibrated relevance percentage; convert it back to a
    logit first when that is the only representation available.
    """
    if raw_score is None:
        return None

    try:
        score = float(raw_score)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(score):
        return None

    if score_is_probability:
        probability = min(max(score, 1e-6), 1.0 - 1e-6)
        score = math.log(probability / (1.0 - probability))

    calibrated = 1.0 / (1.0 + math.exp(-(score - 2.0)))
    return round(min(0.99, max(0.02, calibrated)), 3)


def fastembed_relevance_score(query: str, content: str, raw_score: Optional[float]) -> Optional[float]:
    """Score FastEmbed's bounded reranker output with a lexical evidence guard.

    FastEmbed returns a useful ranking score in the 0--1 range, but it is not a
    calibrated probability.  Weighting it by query-term coverage prevents a
    generic shared term (such as "India") from making an unrelated chunk appear
    relevant while preserving genuinely matching document passages.
    """
    if raw_score is None:
        return None

    try:
        ranking_score = float(raw_score)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(ranking_score):
        return None

    query_terms = {
        token for token in re.findall(r"[a-z0-9]+", query.lower())
        if len(token) > 2 and token not in QUERY_STOP_WORDS
    }
    if not query_terms:
        return round(min(0.99, max(0.02, ranking_score)), 3)

    content_terms = set(re.findall(r"[a-z0-9]+", content.lower()))
    coverage = len(query_terms & content_terms) / len(query_terms)

    # Preserve the reranker's confidence once the passage covers most of the
    # meaningful query terms.  Otherwise, penalize a partial/generic overlap
    # ("India" alone for a question about the President of India, for example).
    guarded_score = ranking_score if coverage >= 0.60 else ranking_score * coverage
    return round(min(0.99, max(0.02, guarded_score)), 3)
