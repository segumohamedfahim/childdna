"""Unit Tests for Incident Analyzer"""
from app.ai.incident_analyzer import analyze, _extract_gender, _extract_age, _extract_emotion, _extract_clothing, _extract_location


class TestIncidentAnalyzer:
    """Test cases for the incident analyzer utility"""

    def test_analyze_full_report(self) -> None:
        """Test complete analysis of a realistic rescue report"""
        result = analyze("Small boy crying near the fountain wearing a blue shirt")
        assert result["gender"] == "male"
        assert result["gender_confidence"] > 0.9
        assert result["emotion"] == "distressed"
        assert result["emotion_confidence"] > 0.8
        assert any("shirt" in item for item in result["clothing"])
        assert result["clothing_confidence"] > 0.7
        assert result["location"] == "fountain"
        assert result["location_confidence"] > 0.8
        assert result["overall_confidence"] > 0.5

    def test_analyze_empty_text(self) -> None:
        """Test analysis with empty text"""
        result = analyze("")
        assert result["gender"] is None
        assert result["gender_confidence"] == 0.0
        assert result["overall_confidence"] == 0.0

    def test_analyze_whitespace_text(self) -> None:
        """Test analysis with whitespace-only text"""
        result = analyze("   ")
        assert result["overall_confidence"] == 0.0

    def test_extract_gender_male(self) -> None:
        """Test gender extraction for male keywords"""
        value, confidence = _extract_gender("a small boy")
        assert value == "male"
        assert confidence > 0.9

    def test_extract_gender_female(self) -> None:
        """Test gender extraction for female keywords"""
        value, confidence = _extract_gender("a little girl")
        assert value == "female"
        assert confidence > 0.9

    def test_extract_gender_none(self) -> None:
        """Test gender extraction with no gender keywords"""
        value, confidence = _extract_gender("the child is missing")
        assert value is None
        assert confidence == 0.0

    def test_extract_age_exact(self) -> None:
        """Test age extraction for exact age"""
        age_min, age_max, confidence = _extract_age("5 years old")
        assert age_min == 5
        assert age_max == 5
        assert confidence > 0.8

    def test_extract_age_range(self) -> None:
        """Test age extraction for age range"""
        age_min, age_max, confidence = _extract_age("4-6 years")
        assert age_min == 4
        assert age_max == 6
        assert confidence > 0.7

    def test_extract_age_keyword(self) -> None:
        """Test age extraction for keyword-based age"""
        age_min, age_max, confidence = _extract_age("a toddler")
        assert age_min == 1
        assert age_max == 3
        assert confidence > 0.8

    def test_extract_age_none(self) -> None:
        """Test age extraction with no age indicators"""
        age_min, age_max, confidence = _extract_age("wearing a red shirt")
        assert age_min is None
        assert age_max is None
        assert confidence == 0.0

    def test_extract_emotion_crying(self) -> None:
        """Test emotion extraction for crying"""
        emotion, confidence = _extract_emotion("child is crying")
        assert emotion == "distressed"
        assert confidence > 0.9

    def test_extract_emotion_happy(self) -> None:
        """Test emotion extraction for happy"""
        emotion, confidence = _extract_emotion("smiling child")
        assert emotion == "happy"
        assert confidence > 0.8

    def test_extract_emotion_none(self) -> None:
        """Test emotion extraction with no emotion keywords"""
        emotion, confidence = _extract_emotion("wearing a blue shirt")
        assert emotion is None
        assert confidence == 0.0

    def test_extract_clothing_single(self) -> None:
        """Test clothing extraction for single item"""
        items, confidence = _extract_clothing("wearing a blue shirt")
        assert len(items) > 0
        assert "shirt" in items[0] or "blue" in items[0]
        assert confidence > 0.7

    def test_extract_clothing_multiple(self) -> None:
        """Test clothing extraction for multiple items"""
        items, confidence = _extract_clothing("blue shirt and red hat")
        assert len(items) >= 1
        assert confidence > 0.7

    def test_extract_clothing_none(self) -> None:
        """Test clothing extraction with no clothing keywords"""
        items, confidence = _extract_clothing("child near the fountain")
        assert len(items) == 0
        assert confidence == 0.0

    def test_extract_location_fountain(self) -> None:
        """Test location extraction for 'near the fountain'"""
        location, confidence = _extract_location("near the fountain")
        assert location == "fountain"
        assert confidence > 0.8

    def test_extract_location_playground(self) -> None:
        """Test location extraction for 'at the playground'"""
        location, confidence = _extract_location("at the playground")
        assert location == "playground"
        assert confidence > 0.8

    def test_extract_location_none(self) -> None:
        """Test location extraction with no location indicators"""
        location, confidence = _extract_location("wearing a blue shirt")
        assert location is None
        assert confidence == 0.0