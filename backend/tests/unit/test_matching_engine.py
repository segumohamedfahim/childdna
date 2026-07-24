"""Unit Tests for Matching Engine"""
from datetime import datetime, timedelta
from app.ai.matching_engine import (
    find_matches,
    compute_similarity,
    categorize,
    recommend,
    MatchResult,
    ALGORITHM_VERSION,
)


class TestMatchingEngine:
    """Test cases for the matching engine"""

    def test_find_matches_returns_sorted_results(self) -> None:
        """Test that find_matches returns results sorted by score descending"""
        source = {
            "incident_id": "src-uuid",
            "gender": "male",
            "gender_confidence": 0.95,
            "estimated_age_min": 4,
            "estimated_age_max": 6,
            "age_confidence": 0.85,
            "clothing": ["blue shirt", "red hat"],
            "clothing_confidence": 0.85,
            "location": "fountain",
            "location_confidence": 0.90,
            "emotion": "distressed",
            "emotion_confidence": 0.90,
            "distinguishing_features": ["mole on cheek"],
            "features_confidence": 0.80,
            "created_at": "2026-07-24T10:00:00",
        }

        candidate_high = source.copy()
        candidate_high["incident_id"] = "candidate-high-uuid"

        candidate_low = source.copy()
        candidate_low["incident_id"] = "candidate-low-uuid"
        candidate_low["gender"] = "female"
        candidate_low["location"] = "other"

        results = find_matches(source, [candidate_low, candidate_high])

        assert len(results) == 2
        assert results[0].similarity_score >= results[1].similarity_score
        assert all(isinstance(r, MatchResult) for r in results)
        assert all(r.match_category for r in results)
        assert all(r.recommendation for r in results)
        assert all(r.score_breakdown for r in results)

    def test_find_matches_empty_candidates(self) -> None:
        """Test find_matches with empty candidate list"""
        source = {
            "incident_id": "src-uuid",
            "gender": "male",
            "gender_confidence": 0.95,
            "created_at": "2026-07-24T10:00:00",
        }
        results = find_matches(source, [])
        assert results == []

    def test_find_matches_identical_incidents(self) -> None:
        """Test find_matches with identical source and candidate"""
        source = {
            "incident_id": "src-uuid",
            "gender": "male",
            "gender_confidence": 1.0,
            "estimated_age_min": 5,
            "estimated_age_max": 5,
            "age_confidence": 1.0,
            "clothing": ["blue shirt"],
            "clothing_confidence": 1.0,
            "location": "fountain",
            "location_confidence": 1.0,
            "emotion": "distressed",
            "emotion_confidence": 1.0,
            "distinguishing_features": ["scar"],
            "features_confidence": 1.0,
            "created_at": "2026-07-24T10:00:00",
        }
        candidate = source.copy()
        candidate["incident_id"] = "candidate-uuid"

        results = find_matches(source, [candidate])
        assert len(results) == 1
        assert results[0].similarity_score > 0.95
        assert results[0].match_category == "identical"

    def test_similarity_gender_match(self) -> None:
        """Test gender similarity comparison"""
        source = {"gender": "male", "gender_confidence": 0.95}
        candidate = {"gender": "male", "gender_confidence": 0.90}

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["gender"]["score"] == 0.90
        assert breakdown["gender"]["contribution"] > 0.0

    def test_similarity_gender_mismatch(self) -> None:
        """Test gender similarity with mismatch"""
        source = {"gender": "male", "gender_confidence": 0.95}
        candidate = {"gender": "female", "gender_confidence": 0.90}

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["gender"]["score"] == 0.0

    def test_similarity_gender_missing(self) -> None:
        """Test gender similarity when one is missing"""
        source = {}
        candidate = {"gender": "male", "gender_confidence": 0.90}

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["gender"]["score"] == 0.0

    def test_similarity_age_overlap(self) -> None:
        """Test age similarity with overlapping ranges"""
        source = {
            "estimated_age_min": 4,
            "estimated_age_max": 6,
            "age_confidence": 0.85,
        }
        candidate = {
            "estimated_age_min": 5,
            "estimated_age_max": 7,
            "age_confidence": 0.80,
        }

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["age"]["score"] == 0.80
        assert breakdown["age"]["contribution"] > 0.0

    def test_similarity_age_no_overlap(self) -> None:
        """Test age similarity with non-overlapping ranges"""
        source = {
            "estimated_age_min": 4,
            "estimated_age_max": 6,
            "age_confidence": 0.85,
        }
        candidate = {
            "estimated_age_min": 10,
            "estimated_age_max": 12,
            "age_confidence": 0.80,
        }

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["age"]["score"] == 0.0

    def test_similarity_clothing_jaccard(self) -> None:
        """Test clothing similarity with Jaccard"""
        source = {
            "clothing": ["blue shirt", "red hat", "jeans"],
            "clothing_confidence": 1.0,
        }
        candidate = {
            "clothing": ["blue shirt", "jeans", "green jacket"],
            "clothing_confidence": 1.0,
        }

        _, breakdown = compute_similarity(source, candidate)
        # Intersection: {blue shirt, jeans} = 2, Union: {blue shirt, red hat, jeans, green jacket} = 4
        # Jaccard = 2/4 = 0.5
        assert breakdown["clothing"]["score"] == 0.5

    def test_similarity_clothing_empty_both(self) -> None:
        """Test clothing similarity when both empty"""
        source = {"clothing": [], "clothing_confidence": 0.0}
        candidate = {"clothing": [], "clothing_confidence": 0.0}

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["clothing"]["score"] == 0.0

    def test_similarity_location_exact(self) -> None:
        """Test location similarity with exact match"""
        source = {"location": "fountain", "location_confidence": 0.90}
        candidate = {"location": "fountain", "location_confidence": 0.85}

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["location"]["score"] == 0.85

    def test_similarity_location_substring(self) -> None:
        """Test location similarity with substring match"""
        source = {"location": "fountain", "location_confidence": 0.90}
        candidate = {"location": "near fountain", "location_confidence": 0.80}

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["location"]["score"] == 0.40  # 0.5 * 0.80

    def test_similarity_location_no_match(self) -> None:
        """Test location similarity with no match"""
        source = {"location": "fountain", "location_confidence": 0.90}
        candidate = {"location": "playground", "location_confidence": 0.85}

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["location"]["score"] == 0.0

    def test_similarity_emotion_match(self) -> None:
        """Test emotion similarity with match"""
        source = {"emotion": "distressed", "emotion_confidence": 0.90}
        candidate = {"emotion": "distressed", "emotion_confidence": 0.85}

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["emotion"]["score"] == 0.85

    def test_similarity_emotion_mismatch(self) -> None:
        """Test emotion similarity with mismatch"""
        source = {"emotion": "distressed", "emotion_confidence": 0.90}
        candidate = {"emotion": "happy", "emotion_confidence": 0.85}

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["emotion"]["score"] == 0.0

    def test_similarity_features_jaccard(self) -> None:
        """Test features similarity with Jaccard"""
        source = {
            "distinguishing_features": ["scar", "mole"],
            "features_confidence": 1.0,
        }
        candidate = {
            "distinguishing_features": ["scar", "birthmark"],
            "features_confidence": 1.0,
        }

        _, breakdown = compute_similarity(source, candidate)
        # Intersection: {scar} = 1, Union: {scar, mole, birthmark} = 3
        # round(1/3, 4) = 0.3333
        assert breakdown["features"]["score"] == 0.3333

    def test_similarity_time_proximity_same(self) -> None:
        """Test time proximity with same time"""
        source = {"created_at": "2026-07-24T10:00:00"}
        candidate = {"created_at": "2026-07-24T10:00:00"}

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["time_proximity"]["score"] == 1.0

    def test_similarity_time_proximity_12h(self) -> None:
        """Test time proximity with 12 hours difference"""
        source = {"created_at": "2026-07-24T10:00:00"}
        candidate = {"created_at": "2026-07-24T22:00:00"}

        _, breakdown = compute_similarity(source, candidate)
        # 1.0 - (12 / 24) = 0.5
        assert breakdown["time_proximity"]["score"] == 0.5

    def test_similarity_time_proximity_24h(self) -> None:
        """Test time proximity with 24 hours difference"""
        source = {"created_at": "2026-07-24T10:00:00"}
        candidate = {"created_at": "2026-07-25T10:00:00"}

        _, breakdown = compute_similarity(source, candidate)
        # 1.0 - (24 / 24) = 0.0
        assert breakdown["time_proximity"]["score"] == 0.0

    def test_similarity_time_missing(self) -> None:
        """Test time proximity when created_at is missing"""
        source = {}
        candidate = {}

        _, breakdown = compute_similarity(source, candidate)
        assert breakdown["time_proximity"]["score"] == 0.0

    def test_categorize_identical(self) -> None:
        """Test categorize returns identical for high scores"""
        assert categorize(0.95) == "identical"
        assert categorize(0.99) == "identical"
        assert categorize(1.00) == "identical"

    def test_categorize_very_high(self) -> None:
        """Test categorize returns very_high"""
        assert categorize(0.85) == "very_high"

    def test_categorize_high(self) -> None:
        """Test categorize returns high"""
        assert categorize(0.70) == "high"

    def test_categorize_medium(self) -> None:
        """Test categorize returns medium"""
        assert categorize(0.50) == "medium"

    def test_categorize_low(self) -> None:
        """Test categorize returns low"""
        assert categorize(0.30) == "low"

    def test_categorize_no_match(self) -> None:
        """Test categorize returns no_match"""
        assert categorize(0.0) == "no_match"

    def test_recommend_no_match(self) -> None:
        """Test recommend for no_match"""
        assert recommend("no_match") == "no_action"

    def test_recommend_low(self) -> None:
        """Test recommend for low"""
        assert recommend("low") == "no_action"

    def test_recommend_medium(self) -> None:
        """Test recommend for medium"""
        assert recommend("medium") == "possible_match"

    def test_recommend_high(self) -> None:
        """Test recommend for high"""
        assert recommend("high") == "likely_match"

    def test_recommend_very_high(self) -> None:
        """Test recommend for very_high"""
        assert recommend("very_high") == "review"

    def test_recommend_identical(self) -> None:
        """Test recommend for identical"""
        assert recommend("identical") == "review"

    def test_recommend_unknown(self) -> None:
        """Test recommend for unknown category"""
        assert recommend("unknown") == "no_action"

    def test_algorithm_version_constant(self) -> None:
        """Test that ALGORITHM_VERSION is set correctly"""
        assert ALGORITHM_VERSION == "rule_engine_v1"