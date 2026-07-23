"""Application Constants - Mission Status, Priority Levels, Token Prefixes"""

# Mission Status Constants
class MissionStatus:
    """Mission status values for rescue operations"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"
    CANCELLED = "cancelled"


# Priority Level Constants
class PriorityLevel:
    """Priority levels for rescue operations"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


# Token Prefix Constants
class TokenPrefix:
    """Token prefixes for different entity types"""
    CHILD_DNA = "cdna_"
    GUARDIAN = "guard_"
    RESCUE_SESSION = "rescue_"
    VERIFICATION = "verify_"


# User Role Constants
class UserRole:
    """User roles in the system"""
    GUARDIAN = "guardian"
    FIRST_HELPER = "first_helper"
    AUTHORITY = "authority"
    ADMIN = "admin"