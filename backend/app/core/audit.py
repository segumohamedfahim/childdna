"""Audit Logging - Structured Security Event Logging"""
from typing import Optional
from app.utils.logger import logger

# Audit action constants
LOGIN_SUCCESS = "LOGIN_SUCCESS"
LOGIN_FAILED = "LOGIN_FAILED"
REGISTER_SUCCESS = "REGISTER_SUCCESS"
PASSWORD_CHANGED = "PASSWORD_CHANGED"
TOKEN_REFRESHED = "TOKEN_REFRESHED"
LOGOUT = "LOGOUT"
LOGOUT_ALL = "LOGOUT_ALL"
ADMIN_USER_UPDATED = "ADMIN_USER_UPDATED"
ADMIN_ROLE_CHANGED = "ADMIN_ROLE_CHANGED"
ADMIN_ACTIVATE_USER = "ADMIN_ACTIVATE_USER"
ADMIN_DEACTIVATE_USER = "ADMIN_DEACTIVATE_USER"
TOKEN_CLEANUP = "TOKEN_CLEANUP"


def audit_log(
    action: str,
    status: str,
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[dict] = None,
) -> None:
    """Log a structured audit event.

    Never logs passwords, JWTs, or refresh tokens.

    Args:
        action: The audit action constant (e.g., LOGIN_SUCCESS).
        status: The outcome status (e.g., "success", "failed").
        user_id: The UUID of the user performing the action (if available).
        email: The email of the user (if available).
        ip_address: The IP address of the request (if available).
        details: Optional additional context (no secrets).
    """
    log_data = {
        "audit": True,
        "action": action,
        "status": status,
    }

    if user_id is not None:
        log_data["user_id"] = user_id
    if email is not None:
        log_data["email"] = email
    if ip_address is not None:
        log_data["ip_address"] = ip_address
    if details is not None:
        log_data["details"] = details

    logger.info(f"Audit: {action}={status}", extra=log_data)


def audit_login_success(
    user_id: str, email: str, ip_address: Optional[str] = None
) -> None:
    """Log a successful login event."""
    audit_log(LOGIN_SUCCESS, "success", user_id=user_id, email=email, ip_address=ip_address)


def audit_login_failed(
    email: str, ip_address: Optional[str] = None
) -> None:
    """Log a failed login attempt."""
    audit_log(LOGIN_FAILED, "failed", email=email, ip_address=ip_address)


def audit_register_success(
    user_id: str, email: str, ip_address: Optional[str] = None
) -> None:
    """Log a successful registration."""
    audit_log(
        REGISTER_SUCCESS, "success",
        user_id=user_id, email=email, ip_address=ip_address,
    )


def audit_password_changed(
    user_id: str, ip_address: Optional[str] = None
) -> None:
    """Log a password change."""
    audit_log(
        PASSWORD_CHANGED, "success",
        user_id=user_id, ip_address=ip_address,
    )


def audit_token_refreshed(
    user_id: str, ip_address: Optional[str] = None
) -> None:
    """Log a token refresh."""
    audit_log(
        TOKEN_REFRESHED, "success",
        user_id=user_id, ip_address=ip_address,
    )


def audit_logout(
    user_id: str, ip_address: Optional[str] = None
) -> None:
    """Log a logout."""
    audit_log(
        LOGOUT, "success",
        user_id=user_id, ip_address=ip_address,
    )


def audit_logout_all(
    user_id: str, count: int, ip_address: Optional[str] = None
) -> None:
    """Log a logout from all sessions."""
    audit_log(
        LOGOUT_ALL, "success",
        user_id=user_id, ip_address=ip_address,
        details={"tokens_revoked": count},
    )


def audit_admin_user_updated(
    admin_id: str, target_user_id: str, ip_address: Optional[str] = None
) -> None:
    """Log an admin user update."""
    audit_log(
        ADMIN_USER_UPDATED, "success",
        user_id=admin_id, ip_address=ip_address,
        details={"target_user_id": target_user_id},
    )


def audit_admin_role_changed(
    admin_id: str, target_user_id: str, new_role: str,
    ip_address: Optional[str] = None,
) -> None:
    """Log an admin role change."""
    audit_log(
        ADMIN_ROLE_CHANGED, "success",
        user_id=admin_id, ip_address=ip_address,
        details={
            "target_user_id": target_user_id,
            "new_role": new_role,
        },
    )


def audit_admin_activate_user(
    admin_id: str, target_user_id: str, ip_address: Optional[str] = None
) -> None:
    """Log an admin user activation."""
    audit_log(
        ADMIN_ACTIVATE_USER, "success",
        user_id=admin_id, ip_address=ip_address,
        details={"target_user_id": target_user_id},
    )


def audit_admin_deactivate_user(
    admin_id: str, target_user_id: str, ip_address: Optional[str] = None
) -> None:
    """Log an admin user deactivation."""
    audit_log(
        ADMIN_DEACTIVATE_USER, "success",
        user_id=admin_id, ip_address=ip_address,
        details={"target_user_id": target_user_id},
    )


def audit_token_cleanup(
    deleted_count: int, ip_address: Optional[str] = None
) -> None:
    """Log a refresh token cleanup."""
    audit_log(
        TOKEN_CLEANUP, "success",
        ip_address=ip_address,
        details={"deleted_count": deleted_count},
    )