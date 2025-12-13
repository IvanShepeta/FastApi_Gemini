import pytest
from jose import jwt

from app.config import settings


def test_root(client):
    """Test root endpoint"""
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "Hello World"}


def test_create_user(client):
    """Test user registration"""
    res = client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "password123"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "created_at" in data


def test_create_user_duplicate_email(client, test_user):
    """Test registration with existing email"""
    res = client.post(
        "/auth/register",
        json={"email": test_user.email, "password": "password123"}
    )
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"].lower()


def test_login_user(client, test_user):
    """Test user login"""
    res = client.post(
        "/auth/login",
        data={"username": test_user.email, "password": "testpassword123"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Verify token payload
    payload = jwt.decode(
        data["access_token"],
        settings.secret_key,
        algorithms=[settings.algorithm]
    )
    assert payload.get("user_id") == test_user.id


def test_login_incorrect_password(client, test_user):
    """Test login with wrong password"""
    res = client.post(
        "/auth/login",
        data={"username": test_user.email, "password": "wrongpassword"}
    )
    assert res.status_code == 403
    assert "invalid credentials" in res.json()["detail"].lower()


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    res = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "password123"}
    )
    assert res.status_code == 403
    assert "invalid credentials" in res.json()["detail"].lower()


def test_get_user(client, test_user):
    """Test get user by ID"""
    res = client.get(f"/auth/user/{test_user.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id


def test_get_nonexistent_user(client):
    """Test get non-existent user"""
    res = client.get("/auth/user/99999")
    assert res.status_code == 404