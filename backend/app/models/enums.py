"""Centralized Enum Classes for Domain Models"""
from enum import Enum


class ChildStatus(str, Enum):
    """Child status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class TokenStatus(str, Enum):
    """Token status enumeration"""
    ISSUED = "issued"
    ACTIVE = "active"
    USED = "used"
    EXPIRED = "expired"
    REVOKED = "revoked"


class SessionStatus(str, Enum):
    """Rescue session status enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"
    CANCELLED = "cancelled"


class EventType(str, Enum):
    """Timeline event type enumeration"""
    INCIDENT_CREATED = "incident_created"
    TOKEN_ACTIVATED = "token_activated"
    RESCUER_ASSIGNED = "rescuer_assigned"
    LOCATION_UPDATED = "location_updated"
    STATUS_CHANGED = "status_changed"
    REUNION_COMPLETED = "reunion_completed"


class GuardianStatus(str, Enum):
    """Guardian status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class MatchCategory(str, Enum):
    """Match category enumeration for incident matching"""
    IDENTICAL = "identical"
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NO_MATCH = "no_match"


class Recommendation(str, Enum):
    """Recommendation enumeration for incident matching"""
    NO_ACTION = "no_action"
    POSSIBLE_MATCH = "possible_match"
    LIKELY_MATCH = "likely_match"
    REVIEW = "review"
