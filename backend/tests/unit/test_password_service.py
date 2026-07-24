"""Unit Tests for Password Service"""
import pytest
from app.services.password_service import PasswordService


class TestPasswordService:
    """Test cases for PasswordService"""

    @pytest.fixture
    def password_service(self) -> PasswordService:
        """Create PasswordService with default rounds"""
        return PasswordService()

    def test_hash_password_returns_string(
        self, password_service: PasswordService
    ) -> None:
        """Test that hash_password returns a non-empty string"""
        hashed = password_service.hash_password("Test@1234")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_starts_with_bcrypt_prefix(
        self, password_service: PasswordService
    ) -> None:
        """Test that bcrypt hash starts with $2b$"""
        hashed = password_service.hash_password("Test@1234")
        assert hashed.startswith("$2b$")

    def test_hash_password_different_for_same_password(
        self, password_service: PasswordService
    ) -> None:
        """Test that same password produces different hashes (salting)"""
        hash1 = password_service.hash_password("Test@1234")
        hash2 = password_service.hash_password("Test@1234")
        assert hash1 != hash2

    def test_verify_password_correct(
        self, password_service: PasswordService
    ) -> None:
        """Test that correct password verifies successfully"""
        password = "Test@1234"
        hashed = password_service.hash_password(password)
        assert password_service.verify_password(password, hashed) is True

    def test_verify_password_incorrect(
        self, password_service: PasswordService
    ) -> None:
        """Test that incorrect password fails verification"""
        hashed = password_service.hash_password("Test@1234")
        assert password_service.verify_password("Wrong@1234", hashed) is False

    def test_verify_password_empty_string(
        self, password_service: PasswordService
    ) -> None:
        """Test that empty password fails verification"""
        hashed = password_service.hash_password("Test@1234")
        assert password_service.verify_password("", hashed) is False

    def test_validate_password_strength_valid(
        self, password_service: PasswordService
    ) -> None:
        """Test that valid password passes all strength checks"""
        is_valid, message = password_service.validate_password_strength(
            "Test@1234"
        )
        assert is_valid is True
        assert message == ""

    def test_validate_password_strength_too_short(
        self, password_service: PasswordService
    ) -> None:
        """Test that short password fails"""
        is_valid, message = password_service.validate_password_strength("Ab1@")
        assert is_valid is False
        assert "8 characters" in message

    def test_validate_password_strength_no_uppercase(
        self, password_service: PasswordService
    ) -> None:
        """Test that password without uppercase fails"""
        is_valid, message = password_service.validate_password_strength(
            "test@1234"
        )
        assert is_valid is False
        assert "uppercase" in message

    def test_validate_password_strength_no_lowercase(
        self, password_service: PasswordService
    ) -> None:
        """Test that password without lowercase fails"""
        is_valid, message = password_service.validate_password_strength(
            "TEST@1234"
        )
        assert is_valid is False
        assert "lowercase" in message

    def test_validate_password_strength_no_digit(
        self, password_service: PasswordService
    ) -> None:
        """Test that password without digit fails"""
        is_valid, message = password_service.validate_password_strength(
            "Test@abcd"
        )
        assert is_valid is False
        assert "digit" in message

    def test_validate_password_strength_no_special(
        self, password_service: PasswordService
    ) -> None:
        """Test that password without special character fails"""
        is_valid, message = password_service.validate_password_strength(
            "Test1234"
        )
        assert is_valid is False
        assert "special" in message