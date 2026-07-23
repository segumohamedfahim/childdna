"""Rescue Rules - Shared Status Transition Validator"""
from typing import Final
from app.models.enums import SessionStatus

# Allowed status transitions as a set of (from_status, to_status) tuples
ALLOWED_TRANSITIONS: Final[set[tuple[SessionStatus, SessionStatus]]] = {
    (SessionStatus.PENDING, SessionStatus.ACTIVE),
    (SessionStatus.PENDING, SessionStatus.CANCELLED),
    (SessionStatus.ACTIVE, SessionStatus.COMPLETE),
    (SessionStatus.ACTIVE, SessionStatus.CANCELLED),
}


def is_transition_allowed(
    current: SessionStatus, new: SessionStatus,
) -> bool:
    """Check if a status transition is valid.

    Args:
        current: The current session status.
        new: The requested new session status.

    Returns:
        bool: True if the transition is allowed.
    """
    if current == new:
        return False
    return (current, new) in ALLOWED_TRANSITIONS