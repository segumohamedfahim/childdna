"""Incident Analyzer - Rule-Based Intelligence Engine

Transforms raw rescue report text into structured attributes using
deterministic NLP, keyword extraction, regex, and rule-based inference.

This module exposes a single public function: analyze(text: str) -> dict

Future AI engines (LLM, Vision, Hybrid) can replace this implementation
by providing a module with the same analyze() signature. No API or
service changes are required.
"""
import re
from typing import Any

# Gender keywords with confidence weights
GENDER_KEYWORDS: dict[str, tuple[str, float]] = {
    "boy": ("male", 0.95),
    "girl": ("female", 0.95),
    "male": ("male", 0.98),
    "female": ("female", 0.98),
    "man": ("male", 0.90),
    "woman": ("female", 0.90),
    "gentleman": ("male", 0.85),
    "lady": ("female", 0.85),
    "son": ("male", 0.85),
    "daughter": ("female", 0.85),
}

# Emotion keywords mapped to emotional states
EMOTION_KEYWORDS: dict[str, tuple[str, float]] = {
    "crying": ("distressed", 0.92),
    "cried": ("distressed", 0.90),
    "cry": ("distressed", 0.88),
    "tears": ("distressed", 0.85),
    "sobbing": ("distressed", 0.95),
    "scared": ("fearful", 0.92),
    "frightened": ("fearful", 0.90),
    "afraid": ("fearful", 0.88),
    "terrified": ("fearful", 0.95),
    "nervous": ("anxious", 0.80),
    "anxious": ("anxious", 0.85),
    "worried": ("anxious", 0.80),
    "upset": ("distressed", 0.80),
    "confused": ("confused", 0.85),
    "lost": ("confused", 0.80),
    "wandering": ("confused", 0.75),
    "happy": ("happy", 0.90),
    "smiling": ("happy", 0.88),
    "calm": ("calm", 0.85),
    "quiet": ("calm", 0.75),
    "angry": ("angry", 0.90),
    "frustrated": ("angry", 0.80),
    "hurt": ("injured", 0.85),
    "injured": ("injured", 0.92),
    "bleeding": ("injured", 0.95),
}

# Clothing keyword list
CLOTHING_KEYWORDS: list[str] = [
    "shirt", "t-shirt", "tshirt", "pants", "jeans", "shorts",
    "dress", "skirt", "jacket", "coat", "sweater", "hoodie",
    "hat", "cap", "shoes", "sneakers", "boots", "sandals",
    "socks", "gloves", "scarf", "belt", "tie", "uniform",
    "pyjamas", "pajamas", "vest", "blazer", "trousers",
    "sweatpants", "leggings", "shorts", "underwear",
    "raincoat", "gown", "robe", "jumper", "cardigan",
    "wristband", "watch", "bracelet", "necklace", "glasses",
]

# Age-related keywords with estimated ranges
AGE_KEYWORDS: dict[str, tuple[int, int, float]] = {
    "infant": (0, 1, 0.80),
    "baby": (0, 2, 0.80),
    "toddler": (1, 3, 0.85),
    "child": (2, 12, 0.70),
    "kid": (2, 12, 0.70),
    "teen": (13, 19, 0.80),
    "teenager": (13, 19, 0.85),
    "adolescent": (13, 19, 0.80),
    "young": (2, 8, 0.65),
    "little": (1, 6, 0.70),
    "small": (1, 6, 0.65),
}

# Preposition keywords for location extraction
LOCATION_PREPOSITIONS: list[str] = [
    "near", "at", "in", "by", "beside", "next to", "behind",
    "under", "on", "opposite", "around", "outside", "inside",
    "between", "among", "alongside",
]


def analyze(text: str) -> dict[str, Any]:
    """Analyze a rescue report and return structured attributes.

    Args:
        text: Raw free-text rescue report.

    Returns:
        dict: Structured analysis matching AnalyzeResponse schema fields.
            Contains gender, estimated_age_min, estimated_age_max, emotion,
            clothing, location, distinguishing_features, and confidence scores.
    """
    if not text or not text.strip():
        return _empty_result()

    text_lower = text.lower()

    gender, gender_conf = _extract_gender(text_lower)
    age_min, age_max, age_conf = _extract_age(text_lower)
    emotion, emotion_conf = _extract_emotion(text_lower)
    clothing, clothing_conf = _extract_clothing(text_lower)
    location, location_conf = _extract_location(text_lower)
    features, features_conf = _extract_features(text, text_lower)

    scores = {
        "gender": gender_conf,
        "age": age_conf,
        "emotion": emotion_conf,
        "clothing": clothing_conf,
        "location": location_conf,
        "features": features_conf,
    }
    overall = _compute_overall_confidence(scores)

    return {
        "gender": gender,
        "gender_confidence": round(gender_conf, 2),
        "estimated_age_min": age_min,
        "estimated_age_max": age_max,
        "age_confidence": round(age_conf, 2),
        "emotion": emotion,
        "emotion_confidence": round(emotion_conf, 2),
        "clothing": clothing,
        "clothing_confidence": round(clothing_conf, 2),
        "location": location,
        "location_confidence": round(location_conf, 2),
        "distinguishing_features": features,
        "features_confidence": round(features_conf, 2),
        "overall_confidence": round(overall, 2),
    }


def _empty_result() -> dict[str, Any]:
    """Return an empty analysis result with zero confidence."""
    return {
        "gender": None,
        "gender_confidence": 0.0,
        "estimated_age_min": None,
        "estimated_age_max": None,
        "age_confidence": 0.0,
        "emotion": None,
        "emotion_confidence": 0.0,
        "clothing": [],
        "clothing_confidence": 0.0,
        "location": None,
        "location_confidence": 0.0,
        "distinguishing_features": [],
        "features_confidence": 0.0,
        "overall_confidence": 0.0,
    }


def _extract_gender(text: str) -> tuple[str | None, float]:
    """Extract gender from text using keyword matching.

    Args:
        text: Lowercase input text.

    Returns:
        tuple: (gender_value, confidence_score).
    """
    for keyword, (value, confidence) in GENDER_KEYWORDS.items():
        if keyword in text:
            return value, confidence
    return None, 0.0


def _extract_age(text: str) -> tuple[int | None, int | None, float]:
    """Extract estimated age range using regex and keyword patterns.

    Args:
        text: Lowercase input text.

    Returns:
        tuple: (age_min, age_max, confidence_score).
    """
    # Try age range FIRST: "X-Y years", "X to Y"
    range_patterns = [
        r"(\d+)\s*[-–to]\s*(\d+)\s*(?:year|yr|yo)s?",
        r"aged?\s*(\d+)\s*[-–to]\s*(\d+)",
    ]
    for pattern in range_patterns:
        match = re.search(pattern, text)
        if match:
            age_min = int(match.group(1))
            age_max = int(match.group(2))
            if 0 <= age_min <= age_max <= 18:
                return age_min, age_max, 0.80

    # Try exact age: "X years old", "X-year-old", "age X"
    age_patterns = [
        r"(\d+)\s*[- ]?\s*(?:year|yr|yo)s?\s*(?:old)?",
        r"aged?\s*(\d+)",
        r"(\d+)\s*(?:year|yr|yo)",
    ]
    for pattern in age_patterns:
        match = re.search(pattern, text)
        if match:
            age = int(match.group(1))
            if 0 <= age <= 18:
                return age, age, 0.85

    # Try keyword-based age inference
    for keyword, (min_age, max_age, confidence) in AGE_KEYWORDS.items():
        if keyword in text:
            return min_age, max_age, confidence

    return None, None, 0.0


def _extract_emotion(text: str) -> tuple[str | None, float]:
    """Extract emotional state from keyword matching.

    Args:
        text: Lowercase input text.

    Returns:
        tuple: (emotion_value, confidence_score).
    """
    best_emotion: str | None = None
    best_confidence = 0.0

    for keyword, (emotion, confidence) in EMOTION_KEYWORDS.items():
        if keyword in text and confidence > best_confidence:
            best_emotion = emotion
            best_confidence = confidence

    return best_emotion, best_confidence


def _extract_clothing(text: str) -> tuple[list[str], float]:
    """Extract clothing descriptions using keyword matching.

    Captures color + clothing item pairs for richer descriptions.

    Args:
        text: Lowercase input text.

    Returns:
        tuple: (list_of_clothing_items, confidence_score).
    """
    found_items: list[str] = []
    color_pattern = r"(?:red|blue|green|black|white|yellow|orange|purple|pink|brown|grey|gray|dark|light|striped|checked|floral)\s+\w+"

    for keyword in CLOTHING_KEYWORDS:
        if keyword in text:
            # Try to find color + keyword context
            color_match = re.search(
                rf"(\w+\s+){{0,2}}{keyword}", text
            )
            if color_match:
                found_items.append(color_match.group(0).strip())
            else:
                found_items.append(keyword)

    if found_items:
        confidence = min(0.85, 0.7 + 0.05 * len(found_items))
        return found_items, confidence

    return [], 0.0


def _extract_location(text: str) -> tuple[str | None, float]:
    """Extract location using preposition + following noun phrase.

    Args:
        text: Original case input text (for proper noun preservation).

    Returns:
        tuple: (location_value, confidence_score).
    """
    text_lower = text.lower()

    for prep in LOCATION_PREPOSITIONS:
        pattern = rf"{re.escape(prep)}\s+(?:the\s+|a\s+|an\s+)?([a-z\s]+?)(?:[,.]|\s+(?:and|wearing|crying|near|at|in|wearing|with)\s|$)"
        match = re.search(pattern, text_lower)
        if match:
            location = match.group(1).strip()
            if location and len(location) > 1:
                return location, 0.85

    return None, 0.0


def _extract_features(
    text: str, text_lower: str
) -> tuple[list[str], float]:
    """Extract distinguishing features not covered by other extractors.

    Captures descriptive phrases like 'has a red backpack',
    'wearing glasses', 'carrying a toy'.

    Args:
        text: Original case input text.
        text_lower: Lowercase input text.

    Returns:
        tuple: (list_of_features, confidence_score).
    """
    features: list[str] = []

    # Pattern: "has/having/carrying/wearing a|an X"
    feature_patterns = [
        r"(?:has|having|carrying|wearing|with)\s+(?:a\s+|an\s+)?([a-z\s]+?)(?:[,.]|\s+and\s|$)",
        r"([a-z\s]+?)\s+(?:strapped|tied|attached)",
    ]
    for pattern in feature_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            phrase = match.strip()
            if phrase and len(phrase) > 2:
                # Skip if already matched as clothing
                is_clothing = any(
                    kw in phrase for kw in CLOTHING_KEYWORDS
                )
                if not is_clothing:
                    features.append(phrase.capitalize())

    if features:
        return features, min(0.75, 0.6 + 0.05 * len(features))
    return [], 0.0


def _compute_overall_confidence(scores: dict[str, float]) -> float:
    """Compute weighted overall confidence from individual scores.

    Weights prioritize attributes that are more reliably extracted.

    Args:
        scores: dict of attribute_name -> confidence_score.

    Returns:
        float: Weighted average confidence score.
    """
    weights = {
        "gender": 0.25,
        "clothing": 0.20,
        "emotion": 0.20,
        "location": 0.20,
        "age": 0.10,
        "features": 0.05,
    }

    weighted_sum = sum(
        scores.get(attr, 0.0) * weight
        for attr, weight in weights.items()
    )
    return weighted_sum