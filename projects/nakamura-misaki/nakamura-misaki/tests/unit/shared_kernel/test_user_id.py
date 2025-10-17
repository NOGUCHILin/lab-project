"""Unit tests for UserId value object"""

import pytest

from src.shared_kernel.domain.value_objects.user_id import UserId


class TestUserId:
    """Test suite for UserId value object"""

    def test_create_user_id(self):
        """Test creating a UserId"""
        user_id = UserId("U12345")

        assert user_id.value == "U12345"
        assert str(user_id) == "U12345"

    def test_user_id_with_empty_string_raises_error(self):
        """Test that empty user ID raises ValueError"""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            UserId("")

    def test_user_id_with_whitespace_only_raises_error(self):
        """Test that whitespace-only user ID raises ValueError"""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            UserId("   ")

    def test_user_id_equality(self):
        """Test UserId equality comparison"""
        user_id1 = UserId("U12345")
        user_id2 = UserId("U12345")
        user_id3 = UserId("U67890")

        assert user_id1 == user_id2
        assert user_id1 != user_id3

    def test_user_id_hash(self):
        """Test UserId can be used in sets and dicts"""
        user_id1 = UserId("U12345")
        user_id2 = UserId("U12345")
        user_id3 = UserId("U67890")

        user_set = {user_id1, user_id2, user_id3}
        assert len(user_set) == 2  # user_id1 and user_id2 are same

        user_dict = {user_id1: "User 1", user_id3: "User 3"}
        assert user_dict[user_id2] == "User 1"  # Same as user_id1

    def test_user_id_is_immutable(self):
        """Test that UserId is immutable (frozen dataclass)"""
        user_id = UserId("U12345")

        with pytest.raises(AttributeError):
            user_id.value = "U67890"  # type: ignore

    def test_user_id_repr(self):
        """Test UserId string representation"""
        user_id = UserId("U12345")

        assert repr(user_id) == "UserId('U12345')"
