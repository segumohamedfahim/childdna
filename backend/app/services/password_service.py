"""Password Service - Hashing and Verification using bcrypt"""
import bcrypt


class PasswordService:
    """Service for password hashing and verification.

    Uses bcrypt with configurable rounds for secure password storage.
    """

    def __init__(self, rounds: int = 12) -> None:
        """Initialize the password service.

        Args:
            rounds: Number of bcrypt rounds (default: 12).
        """
        self.rounds = rounds

    def hash_password(self, plain_password: str) -> str:
        """Hash a plaintext password using bcrypt.

        Args:
            plain_password: The plaintext password to hash.

        Returns:
            str: The bcrypt hash as a UTF-8 string.
        """
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(
            plain_password.encode("utf-8"), salt
        )
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a bcrypt hash.

        Args:
            plain_password: The plaintext password to verify.
            hashed_password: The stored bcrypt hash.

        Returns:
            bool: True if the password matches the hash.
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """Validate password strength against policy rules.

        Rules:
            - Minimum 8 characters
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one digit
            - At least one special character

        Args:
            password: The password to validate.

        Returns:
            tuple[bool, str]: (is_valid, error_message).
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        special_chars = set("!@#$%^&*()_+-=[]{}|;':\",./<>?`~")
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

        return True, ""