"""Matching Engine - Stateless Incident Similarity Engine

Compares a source incident's analysis against candidate analyses
and returns ranked potential matches.

Public interface (FROZEN):

    find_matches(
        source_analysis: dict[str, Any],
        candidate_analyses: list[dict[str, Any]],
    ) -> list[MatchResult]

This interface must never change during Sprint 5.2.
Future AI engines must remain compatible with this contract.
Services, repositories, APIs and tests depend on this stable interface.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


ALGORITHM_VERSION = "rule_engine_v1"

ATTRIBUTE_WEIGHTS: dict[str, float] = {
    "gender": 0.20,
    "age": 0.15,
    "clothing": 0.20,
    "location": 0.15,
    "emotion": 0.10,
    "features": 0.15,
    "time_proximity": 0.05,
}

MATCH_CATEGORIES: dict[str, tuple[float, float]] = {
    "identical": (0.95, 1.00),
    "very_high": (0.85, 0.95),
    "high": (0.70, 0.85),
    "medium": (0.50, 0.70),
    "low": (0.30, 0.50),
    "no_match": (0.00, 0.30),
}

RECOMMENDATIONS: dict[str, str] = {
    "no_match": "no_action",
    "low": "no_action",
    "medium": "possible_match",
    "high": "likely_match",
    "very_high": "review",
    "identical": "review",
}


@dataclass
class MatchResult:
    """Result of comparing a source incident against a candidate."""

    matched_incident_id: str
    similarity_score: float
    match_category: str
    recommendation: str
    score_breakdown: dict


def find_matches(
    source_analysis: dict[str, Any],
    candidate_analyses: list[dict[str, Any]],
) -> list[MatchResult]:
    """Find potential matches for a source incident.

    Compares the source analysis against each candidate analysis
    and returns a list of MatchResult objects sorted by
    similarity_score descending.

    Args:
        source_analysis: Analysis dict for the source incident.
        candidate_analyses: List of analysis dicts for candidate incidents.

    Returns:
        list[MatchResult]: Ranked potential matches.
    """
    results: list[MatchResult] = []

    for candidate in candidate_analyses:
        score, breakdown = compute_similarity(source_analysis, candidate)
        category = categorize(score)
        recommendation = recommend(category)

        results.append(
            MatchResult(
                matched_incident_id=candidate.get("incident_id", ""),
                similarity_score=score,
                match_category=category,
                recommendation=recommendation,
                score_breakdown=breakdown,
            )
        )

    results.sort(key=lambda r: r.similarity_score, reverse=True)
    return results


def compute_similarity(
    source: dict[str, Any],
    candidate: dict[str, Any],
) -> tuple[float, dict]:
    """Compute weighted similarity score and breakdown.

    Args:
        source: Source analysis dict.
        candidate: Candidate analysis dict.

    Returns:
        tuple: (total_score, score_breakdown_dict)
    """
    gender_score = compare_gender(source, candidate)
    age_score = compare_age(source, candidate)
    clothing_score = compare_clothing(source, candidate)
    location_score = compare_location(source, candidate)
    emotion_score = compare_emotion(source, candidate)
    features_score = compare_features(source, candidate)
    time_proximity_score = compare_time(source, candidate)

    breakdown: dict[str, Any] = {}
    total = 0.0

    for attr, weight in ATTRIBUTE_WEIGHTS.items():
        score = locals()[f"{attr}_score"]
        contribution = round(score * weight, 6)
        breakdown[attr] = {
            "score": round(score, 4),
            "weight": weight,
            "contribution": contribution,
        }
        total += contribution

    total = round(total, 6)
    breakdown["total_score"] = total
    breakdown["algorithm_version"] = ALGORITHM_VERSION

    return total, breakdown


def compare_gender(
    source: dict[str, Any], candidate: dict[str, Any],
) -> float:
    """Compare gender between two analyses.

    Returns 1.0 if both genders are equal and non-null, 0.0 otherwise.
    Multiplied by min confidence.
    """
    source_gender = source.get("gender")
    candidate_gender = candidate.get("gender")

    if source_gender is None or candidate_gender is None:
        return 0.0

    if source_gender != candidate_gender:
        return 0.0

    source_conf = source.get("gender_confidence", 0.0) or 0.0
    candidate_conf = candidate.get("gender_confidence", 0.0) or 0.0
    return min(source_conf, candidate_conf)


def compare_age(
    source: dict[str, Any], candidate: dict[str, Any],
) -> float:
    """Compare age ranges between two analyses.

    Returns 1.0 if age ranges overlap, 0.0 otherwise.
    Multiplied by min confidence.
    """
    source_min = source.get("estimated_age_min")
    source_max = source.get("estimated_age_max")
    candidate_min = candidate.get("estimated_age_min")
    candidate_max = candidate.get("estimated_age_max")

    if source_min is None or source_max is None:
        return 0.0
    if candidate_min is None or candidate_max is None:
        return 0.0

    if source_min > source_max or candidate_min > candidate_max:
        return 0.0

    if source_min <= candidate_max and candidate_min <= source_max:
        source_conf = source.get("age_confidence", 0.0) or 0.0
        candidate_conf = candidate.get("age_confidence", 0.0) or 0.0
        return min(source_conf, candidate_conf)

    return 0.0


def compare_clothing(
    source: dict[str, Any], candidate: dict[str, Any],
) -> float:
    """Compare clothing items using Jaccard similarity.

    Returns |intersection| / |union|. Returns 0.0 if both sets
    are empty. Multiplied by min confidence.
    """
    source_clothing = source.get("clothing") or []
    candidate_clothing = candidate.get("clothing") or []

    if not isinstance(source_clothing, list):
        source_clothing = []
    if not isinstance(candidate_clothing, list):
        candidate_clothing = []

    source_set = set(source_clothing)
    candidate_set = set(candidate_clothing)

    if not source_set and not candidate_set:
        return 0.0

    union = source_set | candidate_set
    if not union:
        return 0.0

    intersection = source_set & candidate_set
    jaccard = len(intersection) / len(union)

    source_conf = source.get("clothing_confidence", 0.0) or 0.0
    candidate_conf = candidate.get("clothing_confidence", 0.0) or 0.0
    return jaccard * min(source_conf, candidate_conf)


def compare_location(
    source: dict[str, Any], candidate: dict[str, Any],
) -> float:
    """Compare location between two analyses.

    Returns 1.0 for exact match, 0.5 for substring match,
    0.0 otherwise. Multiplied by min confidence.
    """
    source_loc = source.get("location")
    candidate_loc = candidate.get("location")

    if source_loc is None or candidate_loc is None:
        return 0.0

    source_lower = source_loc.lower().strip()
    candidate_lower = candidate_loc.lower().strip()

    if not source_lower or not candidate_lower:
        return 0.0

    if source_lower == candidate_lower:
        score = 1.0
    elif source_lower in candidate_lower or candidate_lower in source_lower:
        score = 0.5
    else:
        score = 0.0

    source_conf = source.get("location_confidence", 0.0) or 0.0
    candidate_conf = candidate.get("location_confidence", 0.0) or 0.0
    return score * min(source_conf, candidate_conf)


def compare_emotion(
    source: dict[str, Any], candidate: dict[str, Any],
) -> float:
    """Compare emotion between two analyses.

    Returns 1.0 if both emotions are equal and non-null, 0.0 otherwise.
    Multiplied by min confidence.
    """
    source_emotion = source.get("emotion")
    candidate_emotion = candidate.get("emotion")

    if source_emotion is None or candidate_emotion is None:
        return 0.0

    if source_emotion != candidate_emotion:
        return 0.0

    source_conf = source.get("emotion_confidence", 0.0) or 0.0
    candidate_conf = candidate.get("emotion_confidence", 0.0) or 0.0
    return min(source_conf, candidate_conf)


def compare_features(
    source: dict[str, Any], candidate: dict[str, Any],
) -> float:
    """Compare distinguishing features using Jaccard similarity.

    Returns |intersection| / |union|. Returns 0.0 if both sets
    are empty. Multiplied by min confidence.
    """
    source_features = source.get("distinguishing_features") or []
    candidate_features = candidate.get("distinguishing_features") or []

    if not isinstance(source_features, list):
        source_features = []
    if not isinstance(candidate_features, list):
        candidate_features = []

    source_set = set(source_features)
    candidate_set = set(candidate_features)

    if not source_set and not candidate_set:
        return 0.0

    union = source_set | candidate_set
    if not union:
        return 0.0

    intersection = source_set & candidate_set
    jaccard = len(intersection) / len(union)

    source_conf = source.get("features_confidence", 0.0) or 0.0
    candidate_conf = candidate.get("features_confidence", 0.0) or 0.0
    return jaccard * min(source_conf, candidate_conf)


def compare_time(
    source: dict[str, Any], candidate: dict[str, Any],
) -> float:
    """Compare time proximity between two analyses.

    Returns max(0.0, 1.0 - (abs(time_diff_hours) / 24.0)).
    Returns 0.0 if either created_at is missing.
    """
    source_time = source.get("created_at")
    candidate_time = candidate.get("created_at")

    if source_time is None or candidate_time is None:
        return 0.0

    source_dt = _parse_datetime(source_time)
    candidate_dt = _parse_datetime(candidate_time)

    if source_dt is None or candidate_dt is None:
        return 0.0

    diff_seconds = abs((source_dt - candidate_dt).total_seconds())
    diff_hours = diff_seconds / 3600.0

    score = max(0.0, 1.0 - (diff_hours / 24.0))
    return score


def _parse_datetime(value: Any) -> datetime | None:
    """Parse a datetime value from string or datetime object.

    Args:
        value: A datetime object or ISO format string.

    Returns:
        Parsed datetime or None if parsing fails.
    """
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None

    return None


def categorize(score: float) -> str:
    """Map a similarity score to a match category.

    Args:
        score: Similarity score in [0.0, 1.0].

    Returns:
        Category string (identical, very_high, high, medium, low, no_match).
    """
    for category, (low, high) in MATCH_CATEGORIES.items():
        if low <= score < high:
            return category

    if score >= 1.0:
        return "identical"
    return "no_match"


def recommend(category: str) -> str:
    """Map a match category to a recommendation.

    Args:
        category: Match category string.

    Returns:
        Recommendation string (no_action, possible_match, likely_match, review).
    """
    return RECOMMENDATIONS.get(category, "no_action")
