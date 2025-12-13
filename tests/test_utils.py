from app.utils import hash, verify


def test_password_hashing():
    """Test password hashing"""
    password = "mypassword123"
    hashed = hash(password)

    assert hashed != password
    assert len(hashed) > 0
    assert isinstance(hashed, str)


def test_password_verification():
    """Test password verification"""
    password = "mypassword123"
    hashed = hash(password)

    assert verify(password, hashed) is True
    assert verify("wrongpassword", hashed) is False


def test_different_passwords_different_hashes():
    """Test that different passwords produce different hashes"""
    password1 = "password123"
    password2 = "password456"

    hash1 = hash(password1)
    hash2 = hash(password2)

    assert hash1 != hash2


def test_same_password_different_hashes():
    """Test that same password hashed twice produces different hashes (due to salt)"""
    password = "mypassword123"

    hash1 = hash(password)
    hash2 = hash(password)

    # Hashes are different due to random salt
    assert hash1 != hash2

    # But both verify correctly
    assert verify(password, hash1) is True
    assert verify(password, hash2) is True
