"""Pure helpers for converting reranker outputs into citation confidence."""

import math
from typing import Optional


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
