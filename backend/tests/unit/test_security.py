from uuid import uuid4
import pytest

from app.core.security import create_access_token, decode_access_token, hash_password, verify_and_update_password


@pytest.mark.unit
def test_password_hash_round_trip() -> None:
    password = "ValidPassword123!"
    encoded_hash = hash_password(password)
    valid, _ = verify_and_update_password(password, encoded_hash)

    assert encoded_hash != password
    assert valid is True


@pytest.mark.unit
def test_wrong_password_is_rejected() -> None:
    encoded_hash = hash_password("ValidPassword123!")
    valid, _ = verify_and_update_password("WrongPassword123!", encoded_hash)

    assert valid is False


@pytest.mark.unit
def test_access_token_round_trip() -> None:
    user_id = uuid4()
    token = create_access_token(user_id)
    decoded_user_id = decode_access_token(token)

    assert decoded_user_id == user_id